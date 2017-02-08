-- Table definitions for the tournament project.
--
-- Put your SQL 'create table' statements in this file; also 'create view'
-- statements if you choose to use it.
--
-- You can write comments in this file by starting them with two dashes, like
-- these lines here.

-- Drop 'tournament' Database if it exists
DROP DATABASE IF EXISTS tournament;

-- Create Database 'tournament'
CREATE DATABASE tournament;

-- Connect to the Database 'tournament'
\c tournament

-- Drop all tables and view (players, matches and playerstandings)if they already exist
DROP TABLE IF EXISTS players CASCADE;
DROP TABLE IF EXISTS matches CASCADE;
DROP VIEW IF EXISTS playerstandings CASCADE;

-- Create table 'players'
CREATE TABLE players(
    player_id serial PRIMARY KEY,
    player_name text
);

-- Create table 'matches'
CREATE TABLE matches(

    match_id serial PRIMARY KEY,
    winner integer references players(player_id),
    loser integer references players(player_id)
);

-- Create view 'playerstandings' which fetches a list of players sorted by the number of wins
-- and rank. Rank is (wins/(matches + 1)) and is needed to handle scenarios where two players
-- have the same number of wins
CREATE VIEW playerstandings AS
SELECT t3.player_id, t3.player_name, wins, matches
FROM (SELECT t1.player_id, t1.player_name, wins, matches, (wins/(matches + 1.0)) as rank
    FROM
       (SELECT player_id, player_name, count(matches.winner) as wins
        FROM players LEFT JOIN matches
        ON players.player_id = matches.winner
        GROUP BY players.player_id) t1

        INNER JOIN

        (SELECT player_id, count(matches.winner) as matches
        FROM players LEFT JOIN matches
        ON players.player_id = matches.winner OR player_id = loser
        GROUP BY players.player_id) t2

ON t1.player_id = t2.player_id
ORDER BY wins DESC, rank DESC) t3;