# -*- coding: utf-8 -*-

# Actual atmospheric pressure in hPa
#aap = 990 
# Actual temperature in Celsius
#atc = 10
# Height above sea level
#hasl = 500
def adjust_pressure_at_sealevel(aap, atc, hasl):
    """
    Calculate the see level air pressure, using aap - actual pressure,
    atc - ambient air temperature at the measuring point, 
    hasl - altitude above sea level at the measuring point, 
    """
    # Adjusted-to-the-sea barometric pressure
    a2ts = aap + ((aap * 9.80665 * hasl)/(287 * (273 + atc + (hasl/400))))
    return a2ts
    # in standard places (hasl from 100-800 m, temperature from -10 to 35) 
    # is the coeficient something close to hasl/10, meaning simply 
    # a2ts is about  aap + hasl/10

if __name__ == '__main__':
    aap = 962.906
    atc = 25.0 #7.125
    hasl = 569.58
    a2ts = adjust_pressure_at_sealevel(aap, atc, hasl)
    print ('aap: ', aap, ', atc: ', atc,', hasl: ', hasl,', a2ts: ', a2ts)