import aiohttp, asyncio, json, csv
from bs4 import BeautifulSoup

async def get_data(page:int=1,limit:int=100,dump:bool=False):
     
    json_string = f"{{\"cmd\":\"request.get\", \"url\":\"https://cmro.travis-starnes.com/reading-order.php?page={page}&limit={limit}\", \"timeout\":60000}}"
    params = json.loads(json_string)

    async with aiohttp.ClientSession() as session:
        async with session.request('post','http://localhost:8095/v1',json=params) as response:
            print(response.status)
            out = await response.json()
            return out

def parse_response(html):
    soup = BeautifulSoup(html,'html.parser')
    out = []
    for item in soup.find_all('div', class_='list_detail_body'):
        # Place in order the issue takes
        order_no = item.find('div', class_='list_detail_order_block').contents[1].string
        # Grab the series and issue number
        series, issue_no = item.find('div', class_='list_detail_title_block').string.strip('\n\xa0').split('#')
        # Split up pubdate into month and year
        pub_month, pub_year = item.find('div', class_='list_detail_publish_block').string.split('/')
        # Split and clean up the series name into name and year of start
        title = series.split('(')[0]
        series_year = series.split('(')[1].strip(') ')
        tmp = {'id':order_no,'series_title':title,'series_year': series_year,'issue':issue_no.split(' ')[0],'pub_month':pub_month.strip('\n'),'pub_year':pub_year}
        out.append(tmp)
    return out

if __name__ == "__main__":
    loop = asyncio.new_event_loop()
    with open('out.csv','w') as fp:
        fields = ['id','series_title','series_year','issue','pub_month','pub_year']
        writer = csv.DictWriter(fp,fieldnames=fields)
        writer.writeheader()
        for i in range(1,11):
            print(f"Starting page {i}")
            html = loop.run_until_complete(get_data(i,100,False))
            src = html['solution']['response']
            with open(f"./cache/page{i}.html","w") as fp:
                fp.write(src)
            tmp = parse_response(src)
            for item in tmp:
                writer.writerow(item)