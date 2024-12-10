# RepCRec: Project Design Document
## Karan Kumar Gangadhar (kk5409) and Aryaman Shaan (as12046)

[Class Diagram (click to view)](https://ibb.co/dtVx1DK)

## Overview
This project simulates the working of a distributed database with concurrency control, failure, and recovery mechanisms. The implementation comprises five modules: `main_manager.py`, `site_manager.py`, `site_module.py`, `transaction.py`, and `transaction_manager.py`. Below is the detailed structure and description of each file, class, and function. More in-depth documentation for each of the functions is provided as comments in the code.

---

## 1. `main_manager.py`
This file initializes and orchestrates the entire system, parsing user input and delegating tasks to the site and transaction managers.

### **Classes and Functions**
- **`MainManager`**
  - **`__init__`**: Initializes `SiteManager`, `TransactionManager`, and tracks the current time.
  - **`run`**: Accepts user commands via the command line.
  - **`parse_input`**: Parses user input using regex and calls appropriate methods in `TransactionManager` and `SiteManager` to handle commands like `begin(T1)`, `fail(2)`, and `dump()`.

---

## 2. `site_manager.py`
This module manages all sites and handles site-related operations like failure, recovery, and variable management.

### **Classes and Functions**
- **`SiteManager`**
  - **`__init__`**: Initializes 10 `Site` objects and prepares data structures for tracking operations.
  - **`initialize_sites`**: Creates and configures 10 sites.
  - **`return_value`**: Handles read requests, determining variable values or whether a transaction should wait or abort.
  - **`update_site`**: Updates variables across all sites during a commit.
  - **`fail_site`**: Marks a site as failed and updates the read mask for its variables.
  - **`recover_site`**: Recovers a site from failure and checks if any waiting operations can proceed.
  - **`return_read_mask_at_timestamp`**: Retrieves the read mask for a variable at a specific timestamp.
  - **`dump`**: Displays the current state of all sites.

---

## 3. `site_module.py`
Defines the structure and behavior of individual sites in the system.

### **Classes and Functions**
- **`Site`**
  - **`__init__`**: Initializes the site, including variable storage, read/write masks, and failure/recovery tracking.
  - **`initialize_store`**: Configures the initial state of variables stored at the site.
  - **`display_store`**: Outputs the current state of all variables at the site, considering whether the site is live.

---

## 4. `transaction.py`
Defines the structure of a transaction and its associated attributes.

### **Classes and Functions**
- **`Transaction`**
  - **`__init__`**: Initializes transaction attributes, including timestamps, read/write operations, and success status.

---

## 5. `transaction_manager.py`
Implements the logic for transaction lifecycle management, concurrency control, and synchronization.

### **Classes and Functions**
- **`TransactionManager`**
  - **`__init__`**: Manages all transactions, interacts with the `SiteManager`, and tracks dependency graphs.
  - **`begin_transaction`**: Starts a new transaction.
  - **`add_write_operation`**: Records a write operation for a transaction.
  - **`add_read_operation`**: Records a read operation and resolves variable values via the `SiteManager`.
  - **`end_transaction`**: Ends a transaction and either commits or aborts it based on concurrency checks.
  - **`transaction_has_all_reads`**: Checks if a transaction consists only of read operations.
  - **`transaction_is_first_committer`**: Determines if the transaction can safely commit first in overlapping timeframes.
  - **`update_transaction_values`**: Applies all write operations during a transaction's commit.
  - **`check_and_update_graph`**: Updates the synchronization graph and detects cycles.
  - **`find_cycles`**: Detects cycles in the dependency graph.
  - **`remove_from_graph`**: Cleans the graph of references to aborted transactions.

---

## Usage
1. Run the `main_manager.py` file to start the system.
2. Command to run: `python3 main_manager.py < test_file.txt`.
3. It is also possible to provide inputs through the command line. Type `exit` to exit out of the program.

---

## Authors
All functions were jointly authored by **Karan Kumar Gangadhar** and **Aryaman Shaan**.

