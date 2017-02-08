**Tournament Results**

- This project involves writing a Python module that uses the PostgreSQL database to keep track of players and matches in a game tournament.
  The game tournament uses the Swiss system for pairing up players in each round: players are not eliminated, and each player should be paired with another player with the same number of wins, or as close as possible.

**Source Code**
- tournament.sql: This file is used to set up the database schema
- tournament.py: This contains the implementation of the Swiss Tournament and provides access to the database via a library of functions which can add, delete or query data in the database
- tournament_test.py - This is a client program which uses the functions written in the tournament.py module and tests the implementation.

**Quick Start**

- Install Vagrant and VirtualBox
- Start Vagrant: Open cmd/Git bash and go to the Vagrant folder. Use the command vagrant up to launch your vitual machine. Type the command vagrant ssh to log into it
- Connect DB: Go to /vagrant/tournament folder and type psql. Type  \i tournament.sql to run the sql commands in the file. Type \q to exit psql
- Test:  To run the series of tests defined in this test suite, run the program from the command line $ python tournament_test.py. You should be able to see a success message once all your tests have passed
