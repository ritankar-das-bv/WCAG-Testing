# WCAG-Testing
This repository contains the Scripts to run the wcag tests on the application
# Accessibility Testing Script

This Python script automates the process of running accessibility tests on web pages using the Axe accessibility engine through Selenium WebDriver. The script captures accessibility violations based on WCAG (Web Content Accessibility Guidelines) levels 2.0 (A, AA, AAA), and generates JSON reports for each tested page. Additionally, it consolidates these results into a single HTML report, which includes tables and charts for easier analysis.

## Features

- **Automated Accessibility Testing**: Leverages Axe through Selenium to audit web pages for accessibility violations.
- **WCAG 2.0 Compliance**: Supports tests for WCAG levels A, AA, and AAA.
- **Detailed Reporting**: Generates individual JSON reports for each page and WCAG level.
- **Consolidated HTML Report**: Includes visual summaries (bar and pie charts) for WCAG levels and violation severity, as well as detailed violation data.
- **Customizable**: Easily configure which URLs to test and include company branding in reports.

## Requirements

### Python Packages:
- `selenium`: Automates browser interactions.
- `axe-selenium-python`: Runs accessibility audits using the Axe engine.
- `matplotlib`: Generates visual charts.
- `pandas`: Handles and manipulates violation data.
- `json`: Manages JSON reports.
- `datetime`: Adds timestamp information to reports.

### System Dependencies:
- Chrome browser and ChromeDriver (must be installed and configured in the system path).

### Credentials:
- A valid login URL, username, and password to authenticate on the website being tested (if required).

## Installation

1. Clone this repository:
   ```bash
   git clone https://github.com/your-repo/accessibility-testing-script.git

