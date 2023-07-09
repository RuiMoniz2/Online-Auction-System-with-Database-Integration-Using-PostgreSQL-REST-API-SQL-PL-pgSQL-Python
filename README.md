# Online Auction System with Database Integration (Using PostgreSQL, REST API, SQL, PL/pgSQL)
## Project Overview
The goal of this project is to develop an online auction system with a database backend, utilizing PostgreSQL as the transactional DBMS. The system follows a distributed database application architecture and provides a REST API for seamless interaction. The project emphasizes the use of SQL and PL/pgSQL for server-side programming and implements various strategies for managing transactions, concurrency conflicts, and database security.

## Objectives
By completing this project, students will achieve the following objectives:

Understand the organization, planning, and execution of a database application development project.
Master the creation of conceptual and physical data models to support and persist application data.
Design, implement, test, and deploy a database system with PostgreSQL.
Install, configure, manage, and optimize PostgreSQL as the relational DBMS.
Gain proficiency in client and server-side programming using SQL and PL/pgSQL.
Implement error detection, avoidance, and mitigation strategies.
Provide comprehensive documentation for the developed system.
## Features Implemented
The project includes the following features:

User registration and authentication with username and password.
Creation of new auctions, including item selection, minimum price setting, and specifying the end date and time of the auction.
Listing and searching for active auctions based on item codes (EAN/ISBN) or descriptions.
Viewing detailed information about an auction, including item description, end date, messages on the auction board, and bidding history.
Bidding on active auctions with validation to ensure the bid is higher than the minimum price and any previous bids.
Editing auction properties by the seller, maintaining previous versions for reference.
Writing messages on the auction board for communication among participants.
Immediate delivery of notifications to users' inboxes for new messages and outbid notifications.
Automatic termination of auctions at the specified date, time, and minute, determining the winning bidder and closing further bidding.

