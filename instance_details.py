# instance_list.py
# Description: Script to Loop in OCI tenancy compartments and List Instance Inventory with Detailed information
#
import pathlib
import oci
import glob
import os
import datetime
from prettytable import PrettyTable

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
    identity_client = oci.identity.IdentityClient(config)
    blockstorage_client = oci.core.BlockstorageClient(config)
    database_client = oci.database.DatabaseClient(config)

tenant_id = config['tenancy']
# Get Tenant Name from Tenant ID
get_tenancy_response = identity_client.get_tenancy(tenancy_id=tenant_id).data
tenant_name = get_tenancy_response.name

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
# Function Get Boot volume size from boot volume id
def get_boot_volume(instance_id,compartment_id,instance_av):
    list_boot_volume_attachments_response = compute_client.list_boot_volume_attachments(
        availability_domain=instance_av,
        compartment_id=compartment_id,
        instance_id=instance_id).data
    get_boot_volume_response = blockstorage_client.get_boot_volume(
        boot_volume_id=list_boot_volume_attachments_response[0].boot_volume_id).data
    return get_boot_volume_response

# Function Get Database Base Systems
def get_base_databases(compartment_id):
    get_base_databases_response = database_client.list_db_systems(
        compartment_id=compartment_id).data
    return get_base_databases_response

def get_performance_description(performance_value):
    # Check for specific performance levels
    if performance_value == 10:
        return "Balanced"
    elif performance_value == 20:
        return "Higher Performance"
    elif performance_value >= 30:
        return "Ultra High Performance"
    else:
        return "Unknown"

# Function Get Image Name from Image ID
def get_image_name(image_ocid):
    # Retrieve image details
    image = compute_client.get_image(image_id=image_ocid).data
    # Return image display name
    return image.display_name

# Function to get vnic ID from instance ocid and compartment ocid
def get_vnic_id(instance_ocid, compartment_ocid):
    list_vnic_attachments_response = compute_client.list_vnic_attachments(
        compartment_id=compartment_ocid,
        instance_id=instance_ocid,
        limit=10 ).data
    return list_vnic_attachments_response

# Function to get vnic details from vnic ocid
def get_vnic_details(vnic_ocid):
    vnic_ocid_var = vnic_ocid
    core_client = oci.core.VirtualNetworkClient(config)
    pri =[]
    pub = []
    for vnic in vnic_ocid_var:
        vnic_var = core_client.get_vnic(vnic_id=vnic.id).data
        vnic_name = vnic_var.display_name
        vnic_subnetid = vnic_var.subnet_id
        vnic_private_ip = vnic_var.private_ip
        vnic_public_ip = vnic_var.public_ip
        pri.append(vnic_private_ip)
        pub.append(vnic_public_ip)

    return {"vnic_id": vnic.id,
            "vnic_name": vnic.display_name,
            "subnet_id": vnic.subnet_id,
            "private_ip": pri,
            "public_ip": pub}

# Set up table headers
table = PrettyTable()
table.field_names = ["Instance Name", "Compartment", "Private IP", "Public_IP", "image", "Shape", \
                     "Fault Domain", "State", "OCPU", "Memory", "Boot_Volume_Size", "Boot_volume_perf"]

# Get All Compartments and save into Json <tenant-name>-compartment.json
allcompartments = ReadAllCompartments(tenant_id, identity_client, tenant_name)

# Loop for all compartment
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
    # Check Base Database Systems in Compartment
    base_databases=get_base_databases(compartment_ocid)
    if len(base_databases) == 0:
        pass
    else:
        for database in base_databases:
            list_db_nodes_response = database_client.list_db_nodes(compartment_id=compartment_ocid,db_system_id=database.id).data
            for node in list_db_nodes_response:
                get_db_network_details = network_client.get_vnic(node.vnic_id).data
                table.add_row( [database.display_name, compartment_name, get_db_network_details.private_ip, \
                            "N/A", f'Oracle Database Base System {database.version}', database.shape, node.fault_domain, \
                            node.lifecycle_state, node.cpu_core_count, \
                            node.memory_size_in_gbs, database.data_storage_size_in_gbs, "N/A"])

    # Retrieve list of instances
    instances = compute_client.list_instances(compartment_id=compartment_ocid).data
    # If instances list is empty, skip to next compartment
    if not instances:
        continue
    # Loop for all instance details
    for instance in instances:
        vnic_data = get_vnic_id(instance.id, compartment_ocid)
        vnic_list = [network_client.get_vnic(vnic_attachment.vnic_id).data
                    for vnic_attachment in vnic_data]
        public_ip = [i.public_ip for i in vnic_list]
        private_ip = [i.private_ip for i in vnic_list]
        boot_volume_details = get_boot_volume(instance.id, compartment_ocid, instance.availability_domain)
        boot_volume_size = boot_volume_details.size_in_gbs
        boot_volume_perf = get_performance_description(boot_volume_details.vpus_per_gb)
        try:
        #    print(f"image ID: {instance.image_id}")
            image_name = get_image_name(instance.image_id)
        except:
            print("Could not get instance image of instance {instance.display_name}")
            image_name = "-"
        table.add_row( [instance.display_name, compartment_name, private_ip, \
                        public_ip, image_name, instance.shape, instance.fault_domain, \
                        instance.lifecycle_state, instance.shape_config.ocpus, \
                        instance.shape_config.memory_in_gbs, boot_volume_size, boot_volume_perf])
# Sort table by instance name
table.sortby = "Instance Name"

# Filter table by instance state
# table = table.search("State", "running")

# Print table and export to CSV
print(table)
with open(f"./{tenant_name}.instance_details.{formatted_date}.csv", "w") as f:
    f.write(table.get_csv_string())
