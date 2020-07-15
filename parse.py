import yaml 

def main():
    
    with open(r"C:\Users\ajshe\Anaconda3\envs\py2cyto\tps\config.yaml") as config:
        
        param_list = yaml.full_load(config)
        
    print(param_list)
    
if __name__ == "__main__":
    main()