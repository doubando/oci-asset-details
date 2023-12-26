# network.py
# Description: Script to Loop in OCI tenancy compartments and List Networking detailed information
# v.1.0
import pathlib
import oci
import glob
import os
from prettytable import PrettyTable
import datetime

# Get the current date and time
now = datetime.datetime.now()

# Format the date and time as DD.MM.YY.HH.mm
formatted_date = now.strftime("%d.%m.%y.%H.%M")

# Define the path to the 'conf' directory
conf_directory = './conf'

# Search for all '.conf' files in the directory
conf_files = glob.glob(os.path.join(conf_directory, '*.conf'))

# Check if more than one .conf file is found
if len(conf_files) > 1:
    raise Exception("Error: More than one .conf file found in the directory.")
elif len(conf_files) == 0:
    raise Exception("Error: No .conf files found in the directory.")
else:
    # Set up authentication
    config = oci.config.from_file(conf_files[0])
    compute_client = oci.core.ComputeClient(config)
    network_client = oci.core.VirtualNetworkClient(config)
    ociidentity = oci.identity.IdentityClient(config)

tenant_name = config['tenant_name']
tenant_id = config['tenancy']

##-------------------------------------------Functions Definition----------------------------------------
#-----------------------------------------------------------------------------------------------------
# Read All Compartements, Write the output into list of JSON object in compartment.json file
def ReadAllCompartments(tenancy,login,tenantName):
    compartmentlist=oci.pagination.list_call_get_all_results(login.list_compartments,tenancy,
                               access_level="ANY",compartment_id_in_subtree=True)
    compartmentlist.data.append(login.get_compartment(tenancy).data)
    with open(f"Json/{tenantName}-compartment.json", "w") as comp_file:
        comp_file.write("[")
        list_last_index = len(compartmentlist.data)-1
        iteration = 0
        for item in compartmentlist.data:
            comp_file.write("%s\n" % item)
            if iteration != list_last_index:
                comp_file.write(",")
            iteration+=1
        comp_file.write("]")
    return compartmentlist.data
#-----------------------------------------------------------------------------------------------------
# Get VCN Details
def get_vcn_details(compartment_id):
    # Get the list of VCNs in the specified compartment
    vcn_list = network_client.list_vcns(compartment_id).data
    # Process and return VCN details
    vcn_details = []
    for vcn in vcn_list:
        vcn_info = {
            'vcn_name': vcn.display_name,
            'vcn_id': vcn.id,
            'vcn_cidr': vcn.cidr_block,
            'vcn_domain': vcn.vcn_domain_name,
            'vcn_state': vcn.lifecycle_state
        }
        vcn_details.append(vcn_info)
    return vcn_details
#-----------------------------------------------------------------------------------------------------
# Get Subnet Details
def get_subnet_details(config, compartment_id, vcn_ocid):
    subnets = network_client.list_subnets(compartment_id=compartment_id, vcn_id=vcn_ocid).data
    subnet_details = []
    for subnet in subnets:
        details = {
            "Subnet Name": subnet.display_name,
            "Subnet OCID": subnet.id,
            "CIDR Block": subnet.cidr_block,
            "Route Table OCID": subnet.route_table_id,
            "Security List OCIDs": subnet.security_list_ids,
            "Virtual Router IP": subnet.virtual_router_ip
            # Add more attributes as needed
        }
        subnet_details.append(details)
    return subnet_details
#----------------------------------------------------------------------------------
# Get Routing Table Name
def get_routing_table_name(config, rt_ocid):
    try:
        # Get Routing Table by OCID
        rt = network_client.get_route_table(rt_ocid).data
        return rt.display_name
    except oci.exceptions.ServiceError as e:
        print(f"Error retrieving routing table: {e}")
        return None


# ----------------------------------------------------------------------------------
# Get Security List Name
def get_security_list_name(config, sl_ocid):
    # Create a Virtual Network Client
    network_client = oci.core.VirtualNetworkClient(config)

    try:
        # Get Security List by OCID
        sl = network_client.get_security_list(sl_ocid).data
        return sl.display_name
    except oci.exceptions.ServiceError as e:
        print(f"Error retrieving security list: {e}")
        return None

# Set up table headers
table = PrettyTable()
table_subnet = PrettyTable()
table.field_names = ["Compartment","VCN Name", "CIDR Block", "DNS Domain","lifecycle"]
table_subnet.field_names = ["VCN Name", "Subnet Name", "CIDR Block", "Route Table", "Security List", "Virtual Router IP"]

# Get All Compartments and save into Json <tenant-name>-compartment.json
allcompartments = ReadAllCompartments(tenant_id, ociidentity, tenant_name)
for compartment in allcompartments:
    compartment_ocid = compartment.id
    compartment_name = compartment.name
    # Ignore Empty Compartments
    if compartment_ocid is None or compartment.name == "":
        print(f"Compartment None : {compartment.name}")
        continue
    # Ignore Deleted Compartments
    if compartment.lifecycle_state == "DELETED":
        print(f"Compartment Deleted : {compartment.name}")
        continue
    # Retrieve list of vcns
    vcns = get_vcn_details(compartment_ocid)
    for vcn in vcns:
        # Get subnet Details from VCN
        subnets = get_subnet_details(config, compartment_ocid, vcn['vcn_id'])
        table.add_row([compartment_name,\
                       vcn['vcn_name'],\
                       vcn['vcn_cidr'],\
                       vcn['vcn_domain'],\
                       vcn['vcn_state']])
        for subnet in subnets:
            route_table_name=get_routing_table_name(config, subnet['Route Table OCID'])
            security_list_name=get_security_list_name(config, subnet['Security List OCIDs'][0])
            table_subnet.add_row([vcn['vcn_name'],\
                       subnet['Subnet Name'],\
                       subnet['CIDR Block'],\
                       route_table_name, \
                       security_list_name, \
                       subnet['Virtual Router IP'] \
                        ])

# Sort table by vcn name
table.sortby = "VCN Name"
table_subnet.sortby = "VCN Name"

with open(f"./{tenant_name}.{formatted_date}.vcn_details.csv", "w") as f:
    f.write(table.get_csv_string())
with open(f"./{tenant_name}.{formatted_date}.subnet_details.csv", "w") as f:
    f.write(table_subnet.get_csv_string())