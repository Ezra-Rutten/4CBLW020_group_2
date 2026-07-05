# Based on CCHI index median

# General patrol officer 
crime_weights = {
  "Violence and sexual offences": 182,
  "Robbery": 365,
  "Burglary": 365,
  "Possession of weapons": 273.75,
  "Drugs": 5,
  "Criminal damage and arson": 2,
  "Public order": 7.5,
  "Other crime": 10,
  "Other theft": 2,
  "Theft from the person": 2,
  "Vehicle crime": 5,
  "Shoplifting": 1,
  "Bicycle theft": 2,
  "Anti-social behaviour": 19
}

# Specialist 0-10

crime_weights_mental_health = {
  "Violence and sexual offences": 2.5*0.10,
  "Robbery": 0,
  "Burglary": 0,
  "Possession of weapons": 0,
  "Drugs": 2.5*0.18,
  "Criminal damage and arson": 2.5*0.19,
  "Public order": 2.5*0.18,
  "Other crime": 0,
  "Other theft": 0,
  "Theft from the person": 0,
  "Vehicle crime": 0,
  "Shoplifting": 0,
  "Bicycle theft": 0,
  "Anti-social behaviour": 2.5*0.18
}

crime_weights_social_services = {
  "Violence and sexual offences": 4*0.20,
  "Robbery": 0,
  "Burglary": 0,
  "Possession of weapons": 0,
  "Drugs": 1.25*0.10,
  "Criminal damage and arson": 0,
  "Public order": 0,
  "Other crime": 0,
  "Other theft": 0,
  "Theft from the person": 0,
  "Vehicle crime": 0,
  "Shoplifting": 0,
  "Bicycle theft": 0,
  "Anti-social behaviour": 1.25*0.10
}

crime_weights_negotiator = {
  "Violence and sexual offences": 0.75*0.03,
  "Robbery": 0,
  "Burglary": 0,
  "Possession of weapons": 0.75*0.06,
  "Drugs": 0,
  "Criminal damage and arson": 0,
  "Public order": 0.75*0.07,
  "Other crime": 0,
  "Other theft": 0,
  "Theft from the person": 0,
  "Vehicle crime": 0,
  "Shoplifting": 0,
  "Bicycle theft": 0,
  "Anti-social behaviour": 0
}


crime_weights_k9 = {
  "Violence and sexual offences": 0,
  "Robbery": 0,
  "Burglary": 1.25*0.10,
  "Possession of weapons": 1.5*0.11,
  "Drugs": 5*0.38,
  "Criminal damage and arson": 0,
  "Public order": 0,
  "Other crime": 0,
  "Other theft": 0,
  "Theft from the person": 0,
  "Vehicle crime": 1.5*0.13,
  "Shoplifting": 1.5*0.18,
  "Bicycle theft": 0,
  "Anti-social behaviour": 0
}

crime_weights_sfo = {
  "Violence and sexual offences": 5*0.30,
  "Robbery": 4.5*0.30,
  "Burglary": 0,
  "Possession of weapons": 4*0.28,
  "Drugs": 0,
  "Criminal damage and arson": 1*0.08,
  "Public order": 0,
  "Other crime": 0,
  "Other theft": 0,
  "Theft from the person": 0,
  "Vehicle crime": 0,
  "Shoplifting": 0,
  "Bicycle theft": 0,
  "Anti-social behaviour": 0
}