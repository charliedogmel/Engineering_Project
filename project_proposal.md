# Engineering Project - Time To Clean

# Question/need:

### What is the framing question of your analysis, or the purpose of the model/system you plan to build?

The demand for electricity fluctuates up and down constantly, causing power plants to turn on and off, producing more or less emissions. These marginal emissions change every 5 minutes, depending on whether the electricity is supplied from wind farms or solar energy or fossil-fueled power plants. What if we could adjust our electricity demand to coincide with the lower values of the electricity grid's variable emissions rate? A company called WattTime asked that question and developed the proprietary technology and data solutions to empower any smart device to automatically prioritize energy from cleaner sources.

But what about human-driven or non-smart devices like laundry machines or vacuum cleaners? This project aims to use the WattTime data to create an analytics dashboard (given the end-user's location) to determine whether it's a clean time to clean.

### Who benefits from exploring this question or building this model/system?

People committed to reducing their personal contribution to climate change. 

# Data Description:

### What dataset(s) do you plan to use, and how will you obtain the data?

I will use real-time, forecast, and historical marginal emissions data from the WattTime API.

https://www.watttime.org/api-documentation/#introduction

### What is an individual sample/unit of analysis in this project? What characteristics/features do you expect to work with?

An individual unit occurs every 5 minutes and includes:

freq:	      number of seconds the data is valid from point_time

ba:	      balancing authority abbreviation

percent:      integer from 0-100 (clean to dirty) representing the relative realtime marginal emissions intensity

moer:	      Marginal Operating Emissions Rate (MOER) measured in lbs CO2/MWh. This will probably not be available for this project as it's generally only available for PRO subsciptions.

point_time:   ISO8601 UTC date/time format when this data became valid

### If modeling, what will you predict as your target?

I'm not planning to model. With more time, a good model would be time series forecasting.

# Tools:

### How do you intend to meet the tools requirement of the project?

- Data storage tool: SQL or MongoDB database
- Cloud processing and containers: not sure if Google Cloud and/or Docker will be needed
- Big data handling: not sure this will be needed
- Web applications and Model deployment: one of these tools will be used
- Aquisition tools: API
- Visualization tools: python libraries

### Are you planning in advance to need or use additional tools beyond those required?

No

# MVP Goal:

### What would a minimum viable product (MVP) look like for this project?

It will include a sketch of the pipeline, and data ingestion, storage, and testing.