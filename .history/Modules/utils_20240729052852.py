#check if x isn't a number
def not_number(x):
        try: 
            float(x)
            return False
        except ValueError:
            return True