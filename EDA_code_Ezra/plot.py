import json
import pandas as pd
import matplotlib.pyplot as plt

with open("info.json", "r") as f:
    info = json.load(f)

print(info["crimes"]["crimes_per_month"]["Month"].values())

# Ploting Crimes per Month
plt.figure(figsize=(10, 5))
plt.plot(info["crimes"]["crimes_per_month"]["Month"].values(), info["crimes"]["crimes_per_month"]["crime_count"].values())
plt.xlabel("Month")
plt.ylabel("Number of crimes")
plt.title("Total crimes per month")
plt.xticks(rotation=45)
plt.tight_layout()
plt.savefig("figures/crimes_per_month.png", dpi=300)
plt.close() 

# Ploting Type of Crimes 
# Plotting Type of Crimes as a bar chart
plt.figure(figsize=(10, 5))
plt.bar(info["crimes"]["type_of_crimes"]["Crime type"].values(), info["crimes"]["type_of_crimes"]["crime_count"].values())
plt.xlabel("Crime type")
plt.ylabel("Number of crimes")
plt.title("Total crimes per type")
plt.xticks(rotation=45, ha="right")
plt.tight_layout()

plt.savefig("figures/crimes_per_type.png", dpi=300)
plt.close()

# Ploting LSOA

# Ploting Missing data per Month
plt.figure(figsize=(10, 5))
plt.plot(info["missing_data"]["missing_data_month"]["Month"].values(), info["missing_data"]["missing_data_month"]["missing_rows"].values())
plt.xlabel("Month")
plt.ylabel("Number of Crimes Missing")
plt.title("Total Missing Crimes per month")
plt.xticks(rotation=45)
plt.tight_layout()
plt.savefig("figures/crimes_per_month_missing.png", dpi=300)
plt.close() 

# Ploting Missing data per Type
plt.figure(figsize=(10, 5))
plt.bar(info["missing_data"]["missing_data_crime"]["Crime type"].values(), info["missing_data"]["missing_data_crime"]["missing_rows"].values())
plt.xlabel("Crime type")
plt.ylabel("Number of missing crimes")
plt.title("Total missing crimes per type")
plt.xticks(rotation=45, ha="right")
plt.tight_layout()
plt.savefig("figures/crimes_per_type_missing.png", dpi=300)
plt.close()

# Ploting Missing data per Month Procent
plt.figure(figsize=(10, 5))
plt.plot(info["missing_data"]["missing_data_month_procent"]["Month"].values(), info["missing_data"]["missing_data_month_procent"]["missing_percent"].values())
plt.xlabel("Month")
plt.ylabel("Number of Crimes Missing (%)")
plt.ylim([0,100])
plt.title("Total Missing Crimes per month procent")
plt.xticks(rotation=45)
plt.tight_layout()
plt.savefig("figures/crimes_per_month_missing_procent.png", dpi=300)
plt.close() 

# Ploting Missing data per crime type Procent
plt.figure(figsize=(10, 5))
plt.bar(info["missing_data"]["missing_data_crime_type_procent"]["Crime type"].values(), info["missing_data"]["missing_data_crime_type_procent"]["missing_percent"].values())
plt.xlabel("Crime type")
plt.ylabel("Number of Crimes Missing (%)")
plt.ylim([0,100])
plt.title("Total Missing Crimes per Type procent")
plt.xticks(rotation=45, ha="right")
plt.tight_layout()
plt.savefig("figures/crimes_per_type_missing_procent.png", dpi=300)
plt.close() 

# Missing Attributes
plt.figure(figsize=(10, 5))
plt.bar(info["missing_data"]["missing_attributes"]["missing_percent"].keys(), info["missing_data"]["missing_attributes"]["missing_percent"].values())
plt.xlabel("Attribute")
plt.ylabel("Number of Missing Attributes")
plt.ylim([0,100])
plt.title("Total Missing Attributes")
plt.xticks(rotation=45, ha="right")
plt.tight_layout()
plt.savefig("figures/missing_attributer.png", dpi=300)
plt.close() 