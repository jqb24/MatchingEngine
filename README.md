# MatchingEngine
MatchingEngine simulates an electronic exchange that matches trades submitted by random order generation. The orders can be LIMIT, IO or MARKET and have price/time priority for execution. Orders are first ranked according to their price; orders of the same price are then ranked depending on when they were entered. This exchange is simulatied using a TCP server that matches the trades and a pool of trader threads that uses the client TCP connection to the server. Each trader also starts with an initial balance that gets updated as each trade is executed.

To start the matching engine, run ExechangeSimulation.py and modify order inputs and output.
