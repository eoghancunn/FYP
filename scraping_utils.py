import re 

def get_outfile_name(log_dict):
    outfile = re.sub("[ //]", "_", 
            log_dict['route_info']+"_"+str(log_dict['climber_id'])+".json")
    return outfile
