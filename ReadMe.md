# **Oracle Cloud Resource Inventory**  

 Python script to automate the process of gathering detailed information from Oracle Cloud Infrastructure (OCI) involves a series of steps to interact with OCI's comprehensive cloud services. This script primarily focuses on iterating through OCI compartments to extract vital details of compute instances, such as their names, IDs, and states. Leveraging OCI's Python SDK, the script authenticates and connects to the cloud environment, retrieves a list of compartments, and subsequently fetches information about instances within these compartments. Once the data is collected, the script utilizes libraries like Pandas to format and organize this information into a structured and readable format. Finally, the data is exported into an Excel sheet, offering a convenient and efficient way to analyze and store the instance details from various compartments in OCI. This automation not only streamlines the process of data retrieval and documentation but also significantly enhances the efficiency of cloud resource management and oversight.

#### Preliminary Steps:  

Install Python SDK: Run   
`pip install oci prettytable glob  `   

#### instance_details.py output details:  
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
11. [x] Boot Volume Size (GB)
12. [x] Boot Volume Performance

#### network.py output details:  Consists of two output files
A- vcn_details.csv
Compartment,VCN Name,CIDR Block,DNS Domain,lifecycle
1. [x] Compartment
2. [x] VCN Name
3. [x] CIDR Block
4. [x] DNS Domain
5. [x] Lifecycle State

B- subnet_details.csv
1. [x] VCN Name
2. [x] Subnet Name
3. [x] CIDR Block
4. [x] Route Table Name
5. [x] Security List Name
6. [x] Virtual Router IP

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

2- Put API authentication in auth directory or any other directory make sure to point to in configuration file using "key_file" parameter  

#### Output:  

output file is generated as csv file in the same script directory  
  instance_details.py         -->     `<tenantname>`.instance_details.csv      
  network.py                  -->     `<tenantname>`.vcn_details.csv            
  network.py                  -->     `<tenantname>`.subnet_details.csv          
 
 
### Versions:

##### v.0.7.2
* Added Boot Volume size (GB) and Performance (Balanced, High Performance, Ultra High Performance)
* Fixed README

##### v.0.7.1
* extract tenant name from tenant id (no need to provide tenant name in conf file)
* renamed instance script from main.py to instance_details.py  

##### v.0.7  

* ✓ included network.py script that extracts Subnet and Network details on oracle cloud 
* ✓ updated ReadMe  

##### v.0.6    

* ✓ Update all private IP if multiple VNICs assigned to the instance  
* ✓ Add Public IP if VNIC is assigned  
* ✓ Add Subnet and Network information from VNIC  
* ✓ Rename Output CSV to include Tenant name.  

