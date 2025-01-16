# network.py
# Description: Script to Loop in OCI tenancy compartments and List Networking detailed information
import oci
import glob
import os
import pandas as pd
import openpyxl

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

# Get Tenant Name from Tenant ID
tenant_id = config['tenancy']
get_tenancy_response = ociidentity.get_tenancy(tenancy_id=tenant_id).data
tenant_name = get_tenancy_response.name

##-------------------------------------------Functions Definition----------------------------------------
# -----------------------------------------------------------------------------------------------------
# Read All Compartements, Write the output into list of JSON object in compartment.json file
def ReadAllCompartments(tenancy, login, tenantName):
    compartmentlist = oci.pagination.list_call_get_all_results(login.list_compartments, tenancy,
                                                               access_level="ANY", compartment_id_in_subtree=True)
    compartmentlist.data.append(login.get_compartment(tenancy).data)
    with open(f"Json/{tenantName}-compartment.json", "w") as comp_file:
        comp_file.write("[")
        list_last_index = len(compartmentlist.data) - 1
        iteration = 0
        for item in compartmentlist.data:
            comp_file.write("%s\n" % item)
            if iteration != list_last_index:
                comp_file.write(",")
            iteration += 1
        comp_file.write("]")
    return compartmentlist.data
# ----------------------------------------------------------------------------------
# Get Routing Table Name
def get_routing_table_name(rt_ocid):
    try:
        # Get Routing Table by OCID
        rt = network_client.get_route_table(rt_ocid).data
        return rt.display_name
    except oci.exceptions.ServiceError as e:
        print(f"Error retrieving routing table: {e}")
        return None
# ----------------------------------------------------------------------------------
# Get Security List Name
def get_security_list_name(sl_ocid):
    try:
        # Get Security List by OCID
        sl = network_client.get_security_list(sl_ocid).data
        return sl.display_name
    except oci.exceptions.ServiceError as e:
        print(f"Error retrieving security list: {e}")
        return None

# Set up vcn and subnets arrays
vcns = []
subnets = []
# Get All Compartments and save into Json <tenant-name>-compartment.json
allcompartments = ReadAllCompartments(tenant_id, ociidentity, tenant_name)
for compartment in allcompartments:
    compartment_ocid = compartment.id
    compartment_name = compartment.name
    print(f"Network: working with compartment {compartment_name} ...")
    # Ignore Empty Compartments
    if compartment_ocid is None or compartment.name == "":
        print(f"Network: ❌ Compartment None : {compartment.name}")
        continue
    # Ignore Deleted Compartments
    if compartment.lifecycle_state == "DELETED":
        print(f"Network: ❌ Compartment Deleted : {compartment.name}")
        continue
    # Retrieve list of vcns
    vcns_data = network_client.list_vcns(compartment_ocid).data
    for vcn in vcns_data:
        # Get subnet Details from VCN
        subs = network_client.list_subnets(compartment_id=compartment_ocid, vcn_id=vcn.id).data
        vcns.append(
            {
            "Compartment": compartment_name,
            "VCN Name": vcn.display_name,
            "CIDR Block": vcn.cidr_blocks,
            "DNS Domain": vcn.vcn_domain_name,
            "lifecycle": vcn.lifecycle_state,
            "Number of Subnets": len(subs)
            }
        )
        for subnet in subs:
            route_table_name = get_routing_table_name(subnet.route_table_id)
            security_list_name = get_security_list_name(subnet.security_list_ids[0])
            subnets.append(
                {
                    "VCN Name": vcn.display_name,
                    "Subnet Name": subnet.display_name,
                    "CIDR Block": subnet.cidr_block,
                    "Route Table": route_table_name,
                    "Security List": security_list_name,
                    "Virtual Router IP": subnet.virtual_router_ip,
                    "State": subnet.lifecycle_state
                }
            )
    print(f"Network: ✓ completed with compartment {compartment_name}" )
# Get dataframe to main script
def get_dataframe():
    df_vcns = pd.DataFrame(vcns)
    df_subnets = pd.DataFrame(subnets)
    return df_vcns, df_subnets, tenant_name