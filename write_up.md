# The Cleanest Time to Clean
## Or do anything that uses electricity

Melissa Cooper

## Abstract

Have you ever wondered: How can I reduce my carbon footprint while using electricity? The Cleanest Time to Clean is here to help answer that question. Most of our everyday tasks use electricity - laundry, vacuuming, kitchen appliances, eVehicles, gaming, power tools, and more. Is there a way to ensure that the energy you use comes from the cleanest source? Apart from going off-grid, knowing whether your regional electricity grid's MOER (Marginal Operating Emissions Rate) value will be high (bad, lots of dirty emissions) or low (good, low or no emissions) at a certain time of day can determine which times of day to complete those tasks. The Cleanest Time to Clean web app uses those MOER values to help you plan when to complete your electricity-draining tasks.

## Design

The Data Engineering pipeline involved stitching many new (to me) tools together. Using Google Cloud, MongoDB, and cron scheduling, the program queries, ingests, and processes the data to be used for an interactive web app. The source data comes from WattTime's API. WattTime developed the proprietary technology and data solutions to establish current and 24-hour forecasts of MOER values. They provide the information to empower any smart device to automatically prioritize energy from cleaner sources. In this case, we use their values to empower people to make better personal choices and prioritize lower potential emission rates.

After the API queries for the data, the data is ingested into MongoDB. It is then processed automatically into forms specific for each interactive visual on the Streamlit analytics dashboard.

## Data

Without signing an NDA, the data is only available for one electricity grid region in Northern California called CAISO_NORTH. It contains historical values begining in 2018, resulting in 390,000+ datapoints of actual MOER values. There are also 24-hour forecast values that are available from 2021, resulting in 180,000+ datapoints. These databases will grow for as long as the system in production and would be multiplied by the number of regions available. Thinking about this expansion was one reason to use Google Cloud and MongoDB despite the current managable size of the dataset.

## Algorithms

*Processing*

A Linux crontab job is running daily at 8am PST to ingest and process new data and store pre-calculated dataframes for the visualizations.

*Deployment*
  
Streamlit was used to develop the interactive app.

## Tools

- WattTime API and MongoDB for data ingestion
- MongoDB, Numpy, Datetime, and Pandas for data manipulation
- Streamlit, Google Cloud, and crontab on VM for deployment
- Streamlit, Matplotlib, and Seaborn for plotting

## Communication

Presentation, slides, and write-up
