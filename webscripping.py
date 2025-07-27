from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from bs4 import BeautifulSoup
import time
import re
import csv
from urllib.parse import urlparse
import base64
import requests

def setup_driver():
    """ตั้งค่า Chrome driver"""
    options = webdriver.ChromeOptions()
    # options.add_argument('--headless')  # เอาคอมเมนต์ออกถ้าต้องการรันแบบไม่แสดงหน้าต่าง
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    return webdriver.Chrome(options=options)

def get_logo_base64(logo_url):
    """ดาวน์โหลดโลโก้และคืนค่า base64 string"""
    if not logo_url:
        return ""
    
    try:
        response = requests.get(logo_url, timeout=10)
        response.raise_for_status()
        encoded = base64.b64encode(response.content).decode("utf-8")
        return encoded
    except Exception as e:
        print(f"✗ ไม่สามารถดาวน์โหลดโลโก้ {logo_url}: {e}")
        return ""

def extract_course_details(soup):
    """ดึงข้อมูลรายละเอียดหลักสูตรจาก BeautifulSoup object"""
    details = {}
    
    overview_section = soup.find("li", {"id": "overview", "class": "tabs-content"})
    if overview_section:
        dl_element = overview_section.find("dl")
        if dl_element:
            dt_elements = dl_element.find_all("dt")
            dd_elements = dl_element.find_all("dd")
            for dt, dd in zip(dt_elements, dd_elements):
                key = dt.get_text(strip=True)
                value = dd.get_text(strip=True)
                if key and not key.startswith("meta-") and value:
                    details[key] = value
    return details

def extract_university_info(soup):
    """ดึงข้อมูลมหาวิทยาลัยจาก HTML structure"""
    university_info = {}
    t_head = soup.find("div", {"class": "t-head"})
    if t_head:
        h_brand = t_head.find("span", {"class": "h-brand"})
        if h_brand:
            img_tag = h_brand.find("img")
            if img_tag and img_tag.get("alt"):
                university_info["university_logo"] = img_tag.get("src")
            name_span = h_brand.find("span", {"class": "name"})
            if name_span:
                faculty_link = name_span.find("a", href=lambda x: x and "/faculties/" in x)
                if faculty_link:
                    university_info["faculty"] = faculty_link.get_text(strip=True)
                field_link = name_span.find("a", href=lambda x: x and "/fields/" in x)
                if field_link:
                    university_info["field"] = field_link.get_text(strip=True)
                h1_tag = name_span.find("h1")
                if h1_tag:
                    university_info["course_full_name"] = h1_tag.get_text(strip=True)

        # Extract university name from anchor tag
        university_anchor = t_head.find("a", href=lambda x: x and "/universities/" in x)
        if university_anchor:
            university_info["university_name"] = university_anchor.get_text(strip=True)

    return university_info

def search_and_scrape(driver, keyword):
    wait = WebDriverWait(driver, 30)
    results = []
    try:
        driver.get("https://mytcas.com/")
        search_input = wait.until(EC.presence_of_element_located((By.ID, "search")))
        search_input.clear()
        for char in keyword:
            search_input.send_keys(char)
            time.sleep(0.1)
        search_icon = wait.until(EC.element_to_be_clickable((By.CLASS_NAME, "i-search")))
        search_icon.click()
        wait.until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, "li > a[href*='course.mytcas.com']")))
        time.sleep(3)

        course_links = driver.find_elements(By.CSS_SELECTOR, "li > a[href*='course.mytcas.com']")
        print(f"พบ {len(course_links)} หลักสูตรสำหรับคำค้น: {keyword}")

        course_urls = []
        for link in course_links:
            url = link.get_attribute("href")
            if url and "course.mytcas.com" in url:
                parsed = urlparse(url)
                path_parts = parsed.path.strip("/").split("/")
                if (
                    len(path_parts) == 2 and
                    path_parts[0] == "programs" and
                    re.fullmatch(r"\d{14}[A-Z]?", path_parts[1])
                ):
                    course_urls.append(url)

        print(f"ลิงก์หลักสูตรที่ผ่านการกรอง: {len(course_urls)}")

        # เข้าแต่ละหลักสูตร
        for i, course_url in enumerate(course_urls):
            print(f"กำลังเข้าหลักสูตรที่ {i+1}: {course_url}")
            try:
                driver.get(course_url)
                wait.until(EC.presence_of_element_located((By.TAG_NAME, "body")))
                time.sleep(2)
                soup = BeautifulSoup(driver.page_source, "html.parser")

                course_title = ""
                title_element = soup.find("title")
                if title_element:
                    course_title = title_element.get_text(strip=True)

                university_info = extract_university_info(soup)
                course_details = extract_course_details(soup)

                # แปลงโลโก้เป็น base64 แล้วเก็บใน dict
                logo_url = university_info.get("university_logo", "")
                logo_base64 = get_logo_base64(logo_url) if logo_url else ""
                university_info["university_logo_base64"] = logo_base64

                result = {
                    "keyword": keyword,
                    "url": course_url,
                    "title": course_title,
                    "details": course_details,
                    "university_info": university_info
                }

                results.append(result)

                print(f"✓ ดึงข้อมูลเสร็จสิ้น: {course_title[:100]}...")
                print(f"  URL: {course_url}")
                print("  ข้อมูลมหาวิทยาลัย:")
                for key, value in university_info.items():
                    if key != "university_logo_base64":
                        print(f"    {key}: {value}")
                    else:
                        print(f"    {key}: (base64 string length {len(value)})")

            except Exception as e:
                print(f"✗ เกิดข้อผิดพลาดในการดึงข้อมูลจาก {course_url}: {str(e)}")
                continue

    except Exception as e:
        print(f"เกิดข้อผิดพลาดในการค้นหา '{keyword}': {str(e)}")

    return results

def save_results_to_csv(results, filename="mytcas_results.csv"):
    all_keys = set()
    for res in results:
        all_keys.update(res.keys())
        if 'details' in res and isinstance(res['details'], dict):
            all_keys.update(res['details'].keys())
        if 'university_info' in res and isinstance(res['university_info'], dict):
            all_keys.update(res['university_info'].keys())
    all_keys.discard('details')
    all_keys.discard('university_info')

    fieldnames = sorted(all_keys)

    with open(filename, mode="w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()

        for res in results:
            row = {}
            for key in res:
                if key not in ['details', 'university_info']:
                    row[key] = res[key]
            if 'details' in res and isinstance(res['details'], dict):
                for key, value in res['details'].items():
                    row[key] = value
            if 'university_info' in res and isinstance(res['university_info'], dict):
                for key, value in res['university_info'].items():
                    row[key] = value
            filtered_row = {k: row.get(k, "") for k in fieldnames}
            writer.writerow(filtered_row)

    print(f"บันทึกข้อมูลลงไฟล์ {filename} เรียบร้อยแล้ว")

def main():
    driver = setup_driver()
    try:
        keywords = ["วิศวกรรมปัญญาประดิษฐ์",'วิศวกรรมคอมพิวเตอร์']
        all_results = []

        for keyword in keywords:
            print(f"\n{'='*60}")
            print(f"กำลังค้นหา: {keyword}")
            print(f"{'='*60}")
            results = search_and_scrape(driver, keyword)
            all_results.extend(results)
            time.sleep(3)

        print(f"\n{'='*60}")
        print("สรุปผลลัพธ์ทั้งหมด")
        print(f"{'='*60}")

        for i, result in enumerate(all_results, 1):
            print(f"\n{i}. คำค้น: {result['keyword']}")
            print(f"   ลิงก์: {result['url']}")
            print(f"   ชื่อหลักสูตร: {result['title']}")

            print(f"   ข้อมูลมหาวิทยาลัย:")
            for key, value in result.get('university_info', {}).items():
                if key != "university_logo_base64":
                    print(f"     {key}: {value}")
                else:
                    print(f"     {key}: (base64 string length {len(value)})")

            print(f"   รายละเอียดหลักสูตร:")
            for key, value in result.get('details', {}).items():
                print(f"     {key}: {value}")

            print("-" * 80)

        print(f"\nดึงข้อมูลเสร็จสิ้น รวม {len(all_results)} หลักสูตร")

        save_results_to_csv(all_results)

    except Exception as e:
        print(f"เกิดข้อผิดพลาดในการทำงาน: {str(e)}")

    finally:
        driver.quit()


if __name__ == "__main__":
    main()
