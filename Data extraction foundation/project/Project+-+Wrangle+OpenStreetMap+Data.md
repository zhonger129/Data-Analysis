
# Project: Wrangle OpenStreetMap Data

In this project, I shall use Shenzhen City China of OpenStreetMap as source data. Why this city? Because Shenzhen is my working city currently, I am familiar with the city and it's only with 175 MB after uncompress.
I have worked on Data warehourse/data mark for 6 years, therefore, I have rich experience in SQL/Relational database, here, I shall try to use MongoDB to complete the project. 

Download OSM XML from [OpenStreetMap ShenZhen City](https://mapzen.com/data/metro-extracts/metro/shenzhen_china/) and unzip it, then get ready the data file shenzhen_china.osm .


```python
import xml.etree.cElementTree as ET
import codecs
import re
import pprint
from collections import defaultdict
import json

# Shenzhen City, China OpenStreetMap
file_in = "shenzhen_china.osm"

# The pattern to be replaced on "phone" field for country code
country_r = "^[\+]?8?6?0?"

# The pattern to be replaced on "phone" field for area code
area_r = "^755"

# The pattern to be remove from value of amenity
amenity_r = re.compile('[^\w]|_')

#problemchars = re.compile(r'[=\+<>;"\?%#$@\t\r\n]')

# address type mapping to be updated 
mapping = { "St": "Street",
            "road": "Road",
            "Ave": "Avenue",
            "Av": "Avenue",
            "Rd": "Road"
            }

CREATED = [ "version", "changeset", "timestamp", "user", "uid"]


# Audit if the specific tag["k"]
def is_target(tag,k_val):
    return (tag.attrib["k"] == k_val)

"""
This function is to remove country code if the input is China's telephone number (+86/86)
and remvoe area code (e.g. 0755/755) for local phone number of Shenzhen City
return the uniform phone number
"""
def phone_number_reformart(phone_number):
    if phone_number[0:4] == '+852':
        #For HongKong phone number, output country code + phone nbr "+852 XXXXXXXX"
        ph_temp = phone_number.replace('-','').replace(' ','').replace(')','').replace('(','')
        ph_num = ph_temp[0:4] + " " + ph_temp[4:]
    else:
        #For Shenzhen City, China phone number, output phone nbr"XXXXXXXX" without country code and area code
        
        #For non Shenzhen City, China phone number, output area code + phone nbr "XXX XXXXXXXX" 
        #without country code
        ph_num_local = phone_number.replace('-','').replace(' ','').replace(')','').replace('(','')
        ph_num = re.sub(area_r,'',re.sub(country_r,'',ph_num_local))
    
    return ph_num

# audit if it's a problematic address type
def audit_address_type(address_name):
    if address_name.split()[-1] in mapping.keys():
        return True


#Update the street type of streen name to standard
def update_street_type(name, mapping):
    name = name.replace(name.split()[-1],mapping[name.split()[-1]])

    return name

# audit if it's a problematic amenity
def audit_amenity(amenity):
    return amenity_r.findall(amenity)

#remove ';' and '_' from value of amenity
def amenity_update(has_special_chars,amenity):
    for char in has_special_chars:
        return amenity.replace(char,' ')

# Transfer all attribution to dict format(JSON)
def shape_element(elem):    
    node = {}
    pos_v = []
    address_v = {}
    create_v = {}
    node_refs_v = []
    member_v = []

    
    if elem.tag == "node" or elem.tag == "way" or elem.tag == "relation" :
        full_attrib = elem.attrib
        
        node["type"] = elem.tag
        
        for key, value in full_attrib.items():
            if key not in CREATED and key != "lat" and key != "lon":
                node[key] = value
            elif key in CREATED:
                create_v[key] = value
            else:
                if float(full_attrib["lat"]) not in pos_v:
                    pos_v.append(float(full_attrib["lat"]))
                
                if float(full_attrib["lon"]) not in pos_v:
                    pos_v.append(float(full_attrib["lon"]))
                  
        if create_v:
            node["created"] = create_v
        
        if pos_v:
            node["pos"] = pos_v  
            
        for tag in elem.iter("tag"):
            if is_target(tag,"amenity"):
                has_special_chars = []
                has_special_chars = audit_amenity(tag.attrib["v"])
                if has_special_chars:
                    node["amenity"] = amenity_update(has_special_chars,tag.attrib["v"])  
                else:
                    node["amenity"] = tag.attrib["v"]
            
             # Audit and update phone
            elif is_target(tag,"phone"):
                node["phone"] = phone_number_reformart(tag.attrib["v"]) 
                
            # Audit and update address
            elif (tag.attrib["k"].split(":")[0] == "addr"):
                if tag.attrib["k"] == "addr:street":
                    if audit_address_type(tag.attrib["v"]):
                        address_v[tag.attrib["k"].split(":")[1]] = update_street_type(tag.attrib["v"],mapping)
                    else:
                        address_v[tag.attrib["k"].split(":")[1]] = tag.attrib["v"]
                else:
                    address_v[tag.attrib["k"].split(":")[1]] = tag.attrib["v"]
                      
            else:
                node[tag.attrib["k"]] = tag.attrib["v"]
        
        if address_v:
            node["address"] = address_v
            
        for nd in elem.iter("nd"):
            node_refs_v.append(nd.attrib["ref"])
        
        if node_refs_v:
            node["node_refs"] = node_refs_v
            
        for mem in elem.iter("member"):
            member_v.append(mem.attrib)
            
        if member_v:
            node["member"] = member_v

    return node
                  
def process_map(file_in,pretty=False):
    file_out = "{0}.json".format(file_in)
    #data = []
    with codecs.open(file_out, "w") as fo:
        for _, element in ET.iterparse(file_in, events=("start",)):
            el = shape_element(element)
            if el:
                #data.append(el)
                if pretty:
                    fo.write(json.dumps(el, indent=2)+"\n")
                else:
                    fo.write(json.dumps(el) + "\n")
    #return data
    
    
if __name__ == '__main__':
    process_map(file_in,True)
    print "end succesful"

```

    end succesful


### Import the json file into Mongodb


```python
$ mongoimport --db openstreetmap --collection shenzhen --file '/Users/Simon/Desktop/ThinkPad410/DBS/Tasks/Study/Udacity/进阶/数据提取基础/shenzhen_china.osm.json' 
```

2017-12-26T16:13:16.344+0800	connected to: localhost
2017-12-26T16:13:19.341+0800	[#####...................] openstreetmap.shenzhen	55.0MB/245MB (22.4%)
2017-12-26T16:13:22.344+0800	[##########..............] openstreetmap.shenzhen	108MB/245MB (44.0%)
2017-12-26T16:13:25.343+0800	[###############.........] openstreetmap.shenzhen	162MB/245MB (66.3%)
2017-12-26T16:13:28.342+0800	[#####################...] openstreetmap.shenzhen	222MB/245MB (90.6%)
2017-12-26T16:13:29.324+0800	[########################] openstreetmap.shenzhen	245MB/245MB (100.0%)
2017-12-26T16:13:29.324+0800	imported 917521 documents

### Overview of the data

** Size of file **  


```python
245MB 

```

** Number of unique users **


```python
> db.shenzhen.distinct("created.user").length
879

```

**Number of ways**



```python
> db.shenzhen.find({"type":{"$eq":"way"}}).pretty().count()
92677

```

**Number of node**



```python
> db.shenzhen.find({"type":{"$eq":"node"}}).pretty().count()
821393

```

**Number of supermarket of nodes**


```python
> db.shenzhen.find({$and:[{"type":{"$eq":"node"}},{"shop":{"$eq":"supermarket"}}]}).pretty().count()
101

```

**The name which has the most number of supermarket**


```python
db.shenzhen.aggregate(
    [{$match:{$and:[{"type":{"$eq":"node"}},{"shop":{"$eq":"supermarket"}},{"name":{"$ne":null}}]}},     
     {$group:{"_id":{name:"$name"},count:{$sum:1}}},
     {$sort:{count:-1}}]
)
```

{ "_id" : { "name" : "惠康 Wellcome" }, "count" : 4 }
{ "_id" : { "name" : "百佳超級市場 ParknShop" }, "count" : 4 }
{ "_id" : { "name" : "华润万家" }, "count" : 2 }
{ "_id" : { "name" : "Vanguard Supermarket" }, "count" : 2 }
{ "_id" : { "name" : "沃尔玛" }, "count" : 2 }
{ "_id" : { "name" : "Vanguard" }, "count" : 2 }
{ "_id" : { "name" : "百佳 PARKnSHOP" }, "count" : 2 }
{ "_id" : { "name" : "惠康超級市場 Wellcome Supermarket" }, "count" : 2 }
{ "_id" : { "name" : "诚兴生活超市" }, "count" : 1 }
{ "_id" : { "name" : "好一多超市" }, "count" : 1 }
{ "_id" : { "name" : "华润万家（春风店）" }, "count" : 1 }
{ "_id" : { "name" : "購物超市" }, "count" : 1 }
{ "_id" : { "name" : "家家樂超市" }, "count" : 1 }
{ "_id" : { "name" : "便利店" }, "count" : 1 }
{ "_id" : { "name" : "宜百家超市" }, "count" : 1 }
{ "_id" : { "name" : "International" }, "count" : 1 }
{ "_id" : { "name" : "福万家便利超市" }, "count" : 1 }
{ "_id" : { "name" : "华城超市" }, "count" : 1 }
{ "_id" : { "name" : "百佳超級市場 Park'N Shop" }, "count" : 1 }
{ "_id" : { "name" : "华联超市" }, "count" : 1 }
Type "it" for more

#### Other ideas about the dataset

if above inquiry shows all results, I find the supermarket name need to be correct for some of them. for example:

{ "_id" : { "name" : "Wal Mart" }, "count" : 1 }  
{ "_id" : { "name" : "Walmart" }, "count" : 1 }  
{ "_id" : { "name" : "WalMart" }, "count" : 1 }  

The three, actually, is the same one supermarket **Walmart**, but they were inputted by different format, we should improve for data uniformity. 


```python

```
