# **Oracle Cloud Instance Inventory**

#### Preliminary Steps:

Install Python SDK: Run 
pip install oci prettytable glob os

#### The script will include the following output details:
1. [x] display_name
2. [x] compartment_name
3. [x] Private IP [List]
4. [x] Public IP [List]
5. [x] Image Name
6. [x] Instance Shape
7. [x] Fault Domain
8. [x] State (Running or Stopped)
9. [x] OCPU
10. [x] Memory

#### Setup:

1- Create OCI Configuration file inside conf directory, the script will accept any name that ends up with .conf
Example, oci.conf, tenant.conf

below sample configuration file

#### FileName: oci.conf

#### Content:

`[DEFAULT]
user=<user_ocid>
fingerprint=<user_fingerprint>
tenancy=<tenant_ocid>
region=<region>
key_file=./auth/<path_to_private_key_file>
tenant_name=<tenant_name>`

2- Put API authentication in auth directory or any other directory make sure to point to in configuration file using "key_file" parameter

#### Output:

output file is generated as csv file in the same script directory
`<tenantname>.instance_details.csn `

#### Versions:

v.0.6
✓ Update all private IP if multiple VNICs assigned to the instance
✓ Add Public IP if VNIC is assigned
✓ Add Subnet and Network information from VNIC
✓ Rename Output CSV to include Tenant name.