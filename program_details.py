from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from bs4 import BeautifulSoup
import json
import time
import random


def get_details(url, discipline, sub_discipline):
    # Set up Chrome options
    options = Options()
    options.add_argument("--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36")
    #options.binary_location = "/usr/bin/google-chrome"
    #service = Service(executable_path="/usr/local/bin/chromedriver")

    # Launch the browser
    service = Service(ChromeDriverManager().install())

    driver = webdriver.Chrome(service=service, options=options)
    
    driver.maximize_window()

    # Initialize WebDriverWait
    wait = WebDriverWait(driver, 10)

    # URL and credentials
    #login_url = "https://www.mastersportal.com/studies/107805/consumer-analytics-and-marketing-strategy.html?ref=search_card"
    username = "jahirulislam92134@gmail.com"
    password = "banshkhalI@858"

    # Main data dictionary to store all extracted data
    all_data = {}
    all_data['discipline'] = discipline
    all_data['sub_discipline'] = sub_discipline


    try:
        # Navigate to the page
        driver.get(url)

        # Handle login
        try:
            login_button_initial = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, "#LoginButton")))
            login_button_initial.click()

            login_prompt_button = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, ".GoToLoginWrapper button")))
            login_prompt_button.click()

            email_field = wait.until(EC.presence_of_element_located((By.NAME, "Email")))
            password_field = wait.until(EC.presence_of_element_located((By.NAME, "Password")))
            email_field.send_keys(username)
            password_field.send_keys(password)

            submit_button = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, ".DriverButton")))
            submit_button.click()
        except Exception as e:
            print(f"Login failed: {e}")
            all_data['login_error'] = str(e)
            raise  # Exit if login fails

        # Extract Summary
        try:
            summary = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, ".mdc-layout-grid__cell--span-4-desktop")))
            soup = BeautifulSoup(summary.get_attribute("innerHTML"), 'html.parser')
            study_title_element = soup.find('span', class_='StudyTitle')
            study_title = study_title_element.text.strip() if study_title_element else "Not found"
            study_title_url = study_title_element.find('a')['href'] if study_title_element and study_title_element.find('a') else "Not found"
            organization_name = soup.find('a', class_='TextLink Connector js-essential-info-organisation-link').text.strip() if soup.find('a', class_='TextLink Connector js-essential-info-organisation-link') else "Not found"
            degree_tags = [tag.text.strip() for tag in soup.find_all('span', class_='Tag js-tag')] or ["None"]
            breadcrumbs = [item.text.strip() for item in soup.find_all('li', class_='BreadCrumbsItem')] or ["None"]
            all_data['summary'] = {
                "study_title": study_title,
                "organization_name": organization_name,
                "degree_tags": degree_tags,
                "breadcrumbs": breadcrumbs,
                "study_title_url": study_title_url
            }
        except Exception as e:
            print(f"Error extracting summary: {e}")
            all_data['summary'] = {"error": str(e)}

        # Extract Quick Facts
        try:
            quick_state = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "#QuickFacts")))
            soup = BeautifulSoup(quick_state.get_attribute("innerHTML"), 'html.parser')
            quick_facts_data = {}
            quick_facts = soup.find_all('div', class_='QuickFactComponent RowComponent js-quickFactComponent')
            for quick_fact in quick_facts:
                label = quick_fact.find('div', class_='Label').text.strip() if quick_fact.find('div', class_='Label') else "Unknown"
                if label == "Tuition fee":
                    value = quick_fact.find('div', class_='TuitionFeeContainer').text.strip() if quick_fact.find('div', class_='TuitionFeeContainer') else "Not available"
                elif label == "Duration":
                    value = quick_fact.find('span', class_='js-duration').text.strip() if quick_fact.find('span', class_='js-duration') else "Not available"
                elif label in ["Apply date", "Start date"]:
                    value = {}
                    timing_containers = quick_fact.find_all('div', class_='TimingContainer')
                    for tc in timing_containers:
                        if 'js-notAvailable' not in tc.get('class', []):
                            target = tc.get('data-target', 'unknown')
                            time_elem = tc.find('time')
                            value[target] = time_elem.text.strip() if time_elem else "Not available"
                elif label == "Campus location":
                    value = quick_fact.find('div', class_='Value').text.strip() if quick_fact.find('div', class_='Value') else "Not available"
                else:
                    value = "Not processed"
                quick_facts_data[label] = value
            all_data['quick_facts'] = quick_facts_data
        except Exception as e:
            print(f"Error extracting quick facts: {e}")
            all_data['quick_facts'] = {"error": str(e)}

        # Extract About
        try:
            about = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "#StudySummary")))
            soup = BeautifulSoup(about.get_attribute("innerHTML"), 'html.parser')
            program_description = soup.find('p').text.strip() if soup.find('p') else "Not found"
            official_website_url = soup.find('span', class_='OfficialWebsite').find('a')['href'] if soup.find('span', class_='OfficialWebsite') and soup.find('span', class_='OfficialWebsite').find('a') else "Not found"
            all_data['about'] = {
                "program_description": program_description,
                "official_website_url": official_website_url
            }
        except Exception as e:
            print(f"Error extracting about: {e}")
            all_data['about'] = {"error": str(e)}

        # Extract Dynamic Tab Content
        try:
            links = wait.until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, "#ContentSwitcher button")))
        except Exception as e:
            print(f"Error finding content switcher buttons: {e}")
            links = []
            all_data['tabs_error'] = str(e)

        sections = [
            (0, "key_facts", By.CSS_SELECTOR, "#StudyKeyFacts"),
            (1, "study_description", By.CSS_SELECTOR, "#StudyDescription"),
            (2, "programme_structure", By.XPATH, '//*[(@id = "StudyContents")]'),
            (4, "admission_requirements", By.CSS_SELECTOR, "#AdmissionRequirements"),
            (5, "tuition_fees", By.XPATH, '//*[@id="SwitchableContent"]/div[6]/article'),
            (7, "visa_information", By.ID, "VisaInformationContainer"),
            (8, "work_permit", By.CSS_SELECTOR, "#WorkPermitContent")
        ]

        for index, section_name, by_method, locator in sections:
            try:
                if index >= len(links):
                    raise IndexError(f"Button at index {index} not found")
                time.sleep(random.uniform(5, 10))
                links[index].click()
                time.sleep(random.uniform(5, 10))
                section_content = wait.until(EC.presence_of_element_located((by_method, locator)))
                soup = BeautifulSoup(section_content.get_attribute("innerHTML"), 'html.parser')

                if section_name == "key_facts":
                    data = {}
                    for article in soup.find_all('article', class_='FactItem'):
                        title = article.find('h3', class_='FactItemTitle').text.strip() if article.find('h3', class_='FactItemTitle') else "Unknown"
                        if title == 'Duration':
                            data['Duration'] = article.find('span', class_='Duration').text.strip() if article.find('span', class_='Duration') else "Not available"
                        elif title == 'Start dates & application deadlines':
                            data['Start Dates'] = article.find('time', {'data-format': 'MMMM YYYY'}).text.strip() if article.find('time', {'data-format': 'MMMM YYYY'}) else "Not available"
                            data['Application Deadline'] = article.find('time', {'data-format': 'MMM YYYY'}).text.strip() if article.find('time', {'data-format': 'MMM YYYY'}) else "Not available"
                        elif title == 'Language':
                            data['Language'] = article.find('div', class_='Languages FactItemInformation').text.strip() if article.find('div', class_='Languages FactItemInformation') else "Not available"
                            data['IELTS Score'] = article.find('div', class_='IELTSCard').find('div', class_='Score').text.strip() if article.find('div', class_='IELTSCard') and article.find('div', class_='IELTSCard').find('div', class_='Score') else "N/A"
                            data['TOEFL Score'] = article.find('div', class_='TOEFLCard').find('div', class_='Score').text.strip() if article.find('div', class_='TOEFLCard') and article.find('div', class_='TOEFLCard').find('div', class_='Score') else "N/A"
                        elif title == 'Credits':
                            data['Credits'] = article.find('div', class_='FactItemInformation').text.strip() if article.find('div', class_='FactItemInformation') else "Not available"
                        elif title == 'Delivered':
                            data['Delivered'] = article.find('div', class_='FactItemInformation').text.strip() if article.find('div', class_='FactItemInformation') else "Not available"
                        elif title == 'Campus Location':
                            data['Campus Location'] = [li.text.strip() for li in article.find_all('li')] or ["Not available"]
                        elif title == 'Disciplines':
                            data['Disciplines'] = article.find('a', class_='TextOnly', href=lambda x: 'disciplines' in x).text.strip() if article.find('a', class_='TextOnly', href=lambda x: 'disciplines' in x) else "Not available"
                    all_data[section_name] = data

                elif section_name == "study_description":
                    for aside in soup.find_all('aside'):
                        aside.decompose()

                    # Step 2: Collect headings and their associated paragraphs
                    data = {}
                    current_heading = None

                    # Iterate through direct children, looking for headings and paragraphs
                    for tag in soup.find_all(['h2', 'h3', 'h4', 'h5', 'h6', 'p'], recursive=False):
                        if tag.name in ['h2', 'h3', 'h4', 'h5', 'h6']:
                            current_heading = tag.text.strip()
                            data[current_heading] = []
                        elif tag.name == 'p' and current_heading:
                            data[current_heading].append(tag.text.strip())

                    # Step 3: Map collected headings to desired keys based on keywords
                    final_data = {}
                    for heading, paragraphs in data.items():
                        heading_lower = heading.lower()
                        if "overview" in heading_lower or "about" in heading_lower:
                            final_data['About the Program'] = ' '.join(paragraphs)
                        elif "career" in heading_lower:
                            final_data['Careers'] = ' '.join(paragraphs)
                        elif "research areas" in heading_lower:
                            final_data['Research Areas'] = paragraphs  # Keep as list if needed

                    all_data[section_name] = final_data

                elif section_name == "programme_structure":
                    all_data[section_name] = {'Programme Structure': [li.text.strip() for li in soup.find_all('li')] or ["Not available"]}

                elif section_name == "admission_requirements":
                    academic_req = soup.find('article', id='AcademicRequirements').find('p', class_='NoRequirementsInfo').text.strip() if soup.find('article', id='AcademicRequirements') and soup.find('article', id='AcademicRequirements').find('p', class_='NoRequirementsInfo') else "Not found"
                    english_article = soup.find('article', id='EnglishRequirements')
                    english_req = {
                        "IELTS": english_article.find('div', class_='IELTSCard').find('div', class_='Score').text.strip() if english_article and english_article.find('div', class_='IELTSCard') and english_article.find('div', class_='IELTSCard').find('div', class_='Score') else "N/A",
                        "TOEFL": english_article.find('div', class_='TOEFLCard').find('div', class_='Score').text.strip() if english_article and english_article.find('div', class_='TOEFLCard') and english_article.find('div', class_='TOEFLCard').find('div', class_='Score') else "N/A"
                    } if english_article else {"IELTS": "Not found", "TOEFL": "Not found"}
                    other_req = [li.text.strip() for li in soup.find('article', id='OtherRequirements').find_all('li')] if soup.find('article', id='OtherRequirements') and soup.find('article', id='OtherRequirements').find_all('li') else []
                    all_data[section_name] = {
                        "Academic Requirements": academic_req,
                        "English Requirements": english_req,
                        "Other Requirements": other_req
                    }

                elif section_name == "tuition_fees":
                    data = {'Tuition Fees': {}}
                    for fee_type in ['international', 'national', 'local']:
                        li = soup.find('li', {'data-target': fee_type})
                        data['Tuition Fees'][fee_type.capitalize()] = f"{li.find('span', class_='js-currencyAmount').text.strip()} {li.find('span', class_='CurrencyType').text.strip()}" if li and li.find('span', class_='js-currencyAmount') and li.find('span', class_='CurrencyType') else "Not available"
                    living_costs_section = soup.find('section', id='CostOfLivingContainer')
                    data['Living Costs'] = f"{living_costs_section.find('span', class_='Amount').text.strip()} {living_costs_section.find('span', class_='CurrencyDetails').text.strip()}" if living_costs_section and living_costs_section.find('span', class_='Amount') and living_costs_section.find('span', class_='CurrencyDetails') else "Not available"
                    all_data[section_name] = data

                elif section_name == "visa_information":
                    main_div = soup.find('div', class_='MessageNoInformation')
                    if main_div:
                        paragraphs = main_div.find_all('p')
                        all_data[section_name] = {
                            "Heading": main_div.find('h2').text.strip() if main_div.find('h2') else "Not found",
                            "Visa Requirement": paragraphs[0].text.strip() if paragraphs else "Not found",
                            "Introduction": paragraphs[1].text.strip() if len(paragraphs) > 1 else "Not found",
                            "Things to Arrange": [li.text.strip() for li in main_div.find('ul').find_all('li')] if main_div.find('ul') else [],
                            "Additional Information": [p.text.strip() for p in paragraphs[2:]] if len(paragraphs) > 2 else []
                        }
                    else:
                        paragraphs = soup.find_all('p')
                        if paragraphs:
                            data = []
                            for paragraph in paragraphs:
                                visa_info = paragraph.text.strip()
                                data.append(visa_info)
                            all_data[section_name] = data
                        else:
                            all_data[section_name] = {"error": "Visa information container not found"}


                elif section_name == "work_permit":
                    work_permit_container = soup.find('div', class_='WorkPermitContainer')
                    if work_permit_container:
                        work_permit_data = []
                        current_header = None
                        for child in work_permit_container.children:
                            if child.name == 'div' and 'WorkPermitHeader' in child.get('class', []):
                                current_header = child.find('h2').text.strip() if child.find('h2') else "Unknown"
                                work_permit_data.append({'header': current_header, 'sections': []})
                            elif child.name == 'div' and 'WorkPermitContent' in child.get('class', []):
                                section_data = {
                                    'title': child.find('h3').text.strip() if child.find('h3') else "General Information",
                                    'description': child.find('p', class_='Description').text.strip() if child.find('p', class_='Description') else "",
                                    'details': {}
                                }
                                for section in child.find_all('section', class_='WorkPermitSection'):
                                    section_type = section.get('class', [None])[1] if len(section.get('class', [])) > 1 else 'Unknown'
                                    section_data['details'][section_type] = [
                                        {
                                            'header': item.find('h5', class_='Header').text.strip() if item.find('h5', class_='Header') else "",
                                            'value': item.find('p', class_='Value').text.strip() if item.find('p', class_='Value') else "",
                                            'text': item.find('p', class_='Text').text.strip() if item.find('p', class_='Text') else ""
                                        } for item in section.find_all('li', class_='Item')
                                    ]
                                work_permit_data[-1]['sections'].append(section_data) if work_permit_data else work_permit_data.append({'header': 'Unknown', 'sections': [section_data]})
                        all_data[section_name] = work_permit_data
                    else:
                        all_data[section_name] = {"error": "Work permit container not found"}

            except Exception as e:
                print(f"Error extracting {section_name}: {e}")
                all_data[section_name] = {"error": str(e)}

        # Output all collected data as a single JSON
        details = json.dumps(all_data, indent=4)
        #print(details)

    except Exception as e:
        print(f"Critical error: {e}")
        all_data['critical_error'] = str(e)
        print(json.dumps(all_data, indent=4))

    """ finally:
        input("Press Enter to terminate...") """
    driver.quit()
    return details