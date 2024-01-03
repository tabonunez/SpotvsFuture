<h1>SpotvsFuture Bot</h1>

The SpotvsFuture Bot is designed to optimize trading by executing maker orders in the spot market and taker orders in the futures market. This strategy aims to minimize fees and mitigate risk during execution.

<h3> Parameters </h3>
Before using the bot, you need to set the following parameters:


<h5> q (Total Quantity in USDT): </h5>

-  Specify the total quantity you want to trade.
  
<h5> clipA (Clip Order Size): </h5>

- Determine the size of each individual order, independent of the final trading amount.

<h5> symbolA (Spot Symbol): </h5>

- Choose the symbol of the spot pair you want to trade (e.g., XRPUSDT).
  
<h5> fut_symbolA (Futures Symbol): </h5>

- Select the corresponding futures symbol for the chosen spot pair (e.g., XRPUSD_231229). Note that this is set for a $10 futures contract.
  
<h5> hold_spot (Hold Spot Balance): </h5>

- Set to True if you currently hold the spot balance of the symbol, or False if you have no spot balance in the account. This parameter is particularly useful for transferring funds from spot to futures.

<h5> price (Target Price Difference): </h5>

- Specify the target price difference between the spot and futures markets.
  
<h1> Usage</h1>
To use the SpotvsFuture Bot effectively, ensure that you have configured the parameters according to your trading preferences. Execute the bot to initiate the trading strategy and optimize your trading experience.

Feel free to customize the parameters based on your specific trading goals and market conditions.
