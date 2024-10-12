def not_number(x):
        '''
        check if x isn't a number
        '''
        try: 
            float(x)
            return False
        except ValueError:
            return True