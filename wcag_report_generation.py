import re
import matplotlib.pyplot as plt
from selenium import webdriver
from selenium.webdriver.common.by import By
from axe_selenium_python import Axe
import time
import json
import pandas as pd
from datetime import datetime

# Function to sanitize filenames for URLs
def sanitize_filename(url):
    return re.sub(r'[<>:"/\\|?*]', '_', url)

# Function to run accessibility test
def run_accessibility_test(urls, wcag_levels, login_url, username, password, snapapp_logo_url, bluevector_logo_url):
    # Validate WCAG levels
    valid_wcag_levels = ['wcag2a', 'wcag2aa', 'wcag2aaa']
    for wcag_level in wcag_levels:
        if wcag_level not in valid_wcag_levels:
            raise ValueError(f"Invalid WCAG level: {wcag_level}. Please choose from {valid_wcag_levels}.")

    # Set up Chrome WebDriver
    driver = webdriver.Chrome()

    try:
        # Log in to the application
        driver.get(login_url)
        driver.find_element(By.XPATH, "//input[@id='email']").send_keys(username)
        driver.find_element(By.XPATH, "//input[@id='password']").send_keys(password)
        driver.find_element(By.XPATH, "//button[@id='login']").click()
        time.sleep(5)

        # List to store JSON report file names
        json_files = []
        for url in urls:
            driver.get(url)
            axe = Axe(driver)
            axe.inject()

            # Run Axe for each WCAG level
            for wcag_level in wcag_levels:
                results = axe.run({
                    "runOnly": {
                        "type": "tag",
                        "values": [wcag_level]
                    }
                })

                # Save results to a JSON file
                sanitized_url = sanitize_filename(url)
                json_file = f'accessibility_report_{wcag_level}_{sanitized_url}.json'
                axe.write_results(results, json_file)
                json_files.append((json_file, url))

                # Print number of violations
                violations = results['violations']
                print(f'Number of accessibility violations for {wcag_level} on {url}: {len(violations)}')

    finally:
        driver.quit()

    # Generate HTML report with the collected data
    generate_consolidated_html_report(json_files, 'accessibility_report_with_summary_0014.html', snapapp_logo_url, bluevector_logo_url)


# Function to generate the HTML report
def generate_consolidated_html_report(json_files, html_file, snapapp_logo_url, bluevector_logo_url):
    # Violation summary template
    violation_summary = {
        'wcag2a': {'Critical': 0, 'Serious': 0, 'Minor': 0},
        'wcag2aa': {'Critical': 0, 'Serious': 0, 'Minor': 0},
        'wcag2aaa': {'Critical': 0, 'Serious': 0, 'Minor': 0},
    }

    violations_list = []
    for json_file, url in json_files:
        with open(json_file, 'r') as f:
            data = json.load(f)
        
        violations = data.get('violations', [])
        for violation in violations:
            impact = violation['impact'].capitalize()
            wcag_level = json_file.split('_')[2]
            violations_list.append((wcag_level, impact, violation, url))

            # Update violation summary
            if impact in violation_summary[wcag_level]:
                violation_summary[wcag_level][impact] += 1

    # Sort violations by WCAG level
    violations_list.sort(key=lambda x: ('wcag2aaa', 'wcag2aa', 'wcag2a').index(x[0]))

    # Generate the violations table HTML
    violations_list_html = ""
    for wcag_level, impact, violation, url in violations_list:
        html_element = violation['nodes'][0].get('html', '').strip() or 'No HTML element found'
        html_element_escaped = html_element.replace('<', '&lt;').replace('>', '&gt;')

        violations_list_html += f"""
        <tr>
            <td>{violation['id']}</td>
            <td>{wcag_level.upper()}</td>
            <td>{impact}</td>
            <td><pre>{html_element_escaped}</pre></td>
            <td><a href="{url}" target="_blank">{url}</a></td>
        </tr>
        """

    # Generate summary table and charts
    summary_table_html, bar_chart_path, pie_chart_path = generate_charts_and_summary(violation_summary)

    current_date = datetime.now().strftime('%B %d, %Y')

    # HTML template for the report
    html_content = f"""
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Web Accessibility Report</title>
        <style>
            body {{ font-family: Arial, sans-serif; margin: 20px; background-color: #f0f4f7; }}
            h1 {{ color: #333; text-align: left; font-size: 36px; margin-bottom: 5px; }}
            .summary {{ margin-top: 40px; background-color: #e0e0e0; padding: 20px; border-radius: 8px; }}
            table {{ width: 100%; border-collapse: collapse; margin-top: 20px; }}
            th, td {{ border: 1px solid #ddd; padding: 8px; text-align: center; }}
            th {{ background-color: #0056b3; color: white; }}
            .chart-container {{ display: flex; justify-content: space-between; margin-top: 20px; }}
            .chart-container img {{ width: 48%; }}
            .logo-container {{ display: flex; justify-content: space-between; align-items: center; margin-bottom: 20px; }}
            .logo {{ width: 200px; }}
            .violations-table {{ margin-top: 40px; }}
            pre {{ background-color: #f8f8f8; padding: 8px 12px; border-radius: 4px; white-space: pre-wrap; word-wrap: break-word; font-family: Consolas, 'Courier New', monospace; }}
        </style>
    </head>
    <body>
        <div class="logo-container">
            <img src="{snapapp_logo_url}" alt="SnapApp Logo" class="logo">
            <img src="{bluevector_logo_url}" alt="BlueVector Logo" class="logo">
        </div>

        <h1>Web Accessibility Report</h1>
        <p>Date Run: {current_date}</p>
        <p><strong>Domain:</strong> keystoneco.gov</p>
        <p><strong>Page Count:</strong> 10</p>

        <h2>Summary</h2>
        {summary_table_html}
        <div class="chart-container">
            <img src="{bar_chart_path}" alt="Violation Summary Bar Chart">
            <img src="{pie_chart_path}" alt="WCAG Levels Pie Chart">
        </div>

        <h2>Detailed Violations</h2>
        <table class="violations-table">
            <thead>
                <tr>
                    <th>Violation Type</th>
                    <th>WCAG Level</th>
                    <th>Impact</th>
                    <th>HTML Element</th>
                    <th>Page URL</th>
                </tr>
            </thead>
            <tbody>
                {violations_list_html}
            </tbody>
        </table>
    </body>
    </html>
    """

    # Write the HTML file
    with open(html_file, 'w') as f:
        f.write(html_content)

    print(f'Summary HTML report generated: {html_file}')


# Function to generate summary table and charts
def generate_charts_and_summary(violation_summary):
    df = pd.DataFrame(violation_summary).T
    df = df.apply(pd.to_numeric)
    wcag_totals = df.sum(axis=1)
    summary_table_html = df.to_html(classes='summary-table', header=True)

    # Generate bar chart
    bar_chart_path = 'violation_summary_chart.png'
    df.plot(kind='bar', stacked=True, color=['#DB4437', '#F4B400', '#4285F4'])
    plt.title('Violation Summary by WCAG Level and Impact')
    plt.xlabel('WCAG Level')
    plt.ylabel('Number of Violations')
    plt.xticks(rotation=0)
    plt.savefig(bar_chart_path)
    plt.close()

    # Generate pie chart
    pie_chart_path = 'wcag_levels_chart.png'
    wcag_totals.plot(kind='pie', autopct='%1.1f%%', startangle=90, colors=['#3366cc', '#dc3912', '#ff9900'])
    plt.title('WCAG Levels Distribution')
    plt.ylabel('')
    plt.savefig(pie_chart_path)
    plt.close()

    return summary_table_html, bar_chart_path, pie_chart_path




run_accessibility_test(
    urls=[
        'https://prod-oy2utcpgbq-uc.a.run.app/page/licensing-home?app=94e2c7ee-13e0-48f9-8893-44b5f5ea6490',
        'https://prod-oy2utcpgbq-uc.a.run.app/profile?app=94e2c7ee-13e0-48f9-8893-44b5f5ea6490',
        'https://prod-oy2utcpgbq-uc.a.run.app/create-view/db724699-fe09-4827-b6cb-2b45c9d56ae5?app=94e2c7ee-13e0-48f9-8893-44b5f5ea6490',
        'https://prod-oy2utcpgbq-uc.a.run.app/list/my-complaints-status?app=94e2c7ee-13e0-48f9-8893-44b5f5ea6490',
        'https://prod-oy2utcpgbq-uc.a.run.app/page/keystone-short-term-rental?app=94e2c7ee-13e0-48f9-8893-44b5f5ea6490',
        'https://keystoneco.gov/list/my-str-license-status',
        'https://prod-oy2utcpgbq-uc.a.run.app/filter/50f0a525-358e-40a1-9cbc-f1fa0d5ad149?app=94e2c7ee-13e0-48f9-8893-44b5f5ea6490',
        'https://prod-oy2utcpgbq-uc.a.run.app/create-view/496403d7-db02-4ff0-b1fe-83be67a21b3b?app=94e2c7ee-13e0-48f9-8893-44b5f5ea6490',
        'https://prod-oy2utcpgbq-uc.a.run.app/page/keystone-liquor-license?app=94e2c7ee-13e0-48f9-8893-44b5f5ea6490',
        'https://prod-oy2utcpgbq-uc.a.run.app/filter-view/d826d46c-ffda-42e9-8d64-7f665bd8d700?app=94e2c7ee-13e0-48f9-8893-44b5f5ea6490',
        'https://prod-oy2utcpgbq-uc.a.run.app/create-view/4ddcbf31-d796-495e-84b3-bca905cd5380?app=94e2c7ee-13e0-48f9-8893-44b5f5ea6490',
        'https://prod-oy2utcpgbq-uc.a.run.app/list/my-liquor-license-status?app=94e2c7ee-13e0-48f9-8893-44b5f5ea6490',
        'https://prod-oy2utcpgbq-uc.a.run.app/filter-view/7e628993-d0f3-435b-b2f2-92db82b3ea4a?app=94e2c7ee-13e0-48f9-8893-44b5f5ea6490',
        'https://prod-oy2utcpgbq-uc.a.run.app/filter/search-for-tobacco-licences/stash/716fdf71-f777-4fe6-afec-aafa0db54da5?app=94e2c7ee-13e0-48f9-8893-44b5f5ea6490',
        'https://prod-oy2utcpgbq-uc.a.run.app/list/my-tobacco-license-status?app=94e2c7ee-13e0-48f9-8893-44b5f5ea6490',
        'https://prod-oy2utcpgbq-uc.a.run.app/page/keystone-tobacco-license?app=94e2c7ee-13e0-48f9-8893-44b5f5ea6490',
        'https://keystoneco.gov/create-view/11ba79fc-cd94-41c9-9ff8-499f134d4293?next=%2Fdetail-view%2Ftobacco_licenses%2F%5B%5Bid%5D%5D&app=94e2c7ee-13e0-48f9-8893-44b5f5ea6490'
    ],
    wcag_levels=['wcag2a', 'wcag2aa', 'wcag2aaa'],
    login_url='https://prod-oy2utcpgbq-uc.a.run.app/login',
    username='paulsayantani19@gmail.com',
    password='Sayantani04#',
    snapapp_logo_url= 'https://storage.googleapis.com/snapapp/images/Pages/wcag/SnapApp_logo%2Bmark_white_bg%20(1).png',
    bluevector_logo_url= 'https://storage.googleapis.com/snapapp/images/Pages/wcag/bluevector_logo_ted.png'
)
