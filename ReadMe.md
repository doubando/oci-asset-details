# **Oracle Cloud Instance Inventory**  

 Python script to automate the process of gathering detailed information from Oracle Cloud Infrastructure (OCI) involves a series of steps to interact with OCI's comprehensive cloud services. This script primarily focuses on iterating through OCI compartments to extract vital details of compute instances, such as their names, IDs, and states. Leveraging OCI's Python SDK, the script authenticates and connects to the cloud environment, retrieves a list of compartments, and subsequently fetches information about instances within these compartments. Once the data is collected, the script utilizes libraries like Pandas to format and organize this information into a structured and readable format. Finally, the data is exported into an Excel sheet, offering a convenient and efficient way to analyze and store the instance details from various compartments in OCI. This automation not only streamlines the process of data retrieval and documentation but also significantly enhances the efficiency of cloud resource management and oversight.

#### Preliminary Steps:  

Install Python SDK: Run   
`pip install oci prettytable glob  `   

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

[DEFAULT]  
user=<user_ocid>  
fingerprint=<user_fingerprint>  
tenancy=<tenant_ocid>  
region= <oci_region>  
key_file=./auth/<path_to_private_key_file>  
tenant_name=<tenant_name>  

2- Put API authentication in auth directory or any other directory make sure to point to in configuration file using "key_file" parameter  

#### Output:  

output file is generated as csv file in the same script directory  
`<tenantname>.instance_details.csv `  

#### Versions:  

v.0.6  
* ✓ Update all private IP if multiple VNICs assigned to the instance  
* ✓ Add Public IP if VNIC is assigned  
* ✓ Add Subnet and Network information from VNIC  
* ✓ Rename Output CSV to include Tenant name.  