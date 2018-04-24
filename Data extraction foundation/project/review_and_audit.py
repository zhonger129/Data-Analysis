import xml.etree.cElementTree as ET

# Shenzhen City, China OpenStreetMap
file_in = "shenzhen_china.osm"

phone_nums, addr_street_names, amenitys = [], [], []

all_d = {"Phone":phone_nums,"addr:street":addr_street_names,"amenity":amenitys}

def print_element(all_d):
    for k,v in all_d.items():
        for i in v:
            print "%s : %s" % (k,i)
        
def review_initial_file(element):
    
    if element.tag == "tag":
        #Check given phone number
        if element.attrib["k"] == "phone":
            if element.attrib["v"] not in phone_nums:
                phone_nums.append(element.attrib["v"])
        
        #Check address street type
        if element.attrib["k"] == "addr:street":
            if element.attrib["v"] not in addr_street_names:
                addr_street_names.append(element.attrib["v"])
        
        #Check amenity
        if element.attrib["k"] == "amenity":
            if element.attrib["v"] not in amenitys:
                amenitys.append(element.attrib["v"])


def process_file(file_in):
    for event, element in ET.iterparse(file_in, events=("start",)):
        review_initial_file(element)
        
if __name__ == '__main__':
    process_file(file_in) 
    print_element(all_d)  
    
    print "Completed!!!"
