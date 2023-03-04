import requests
import bs4
import time
from operator import itemgetter
import pandas as pd
from gu import Ui_MainWindow
from PyQt5 import QtWidgets
from PyQt5.QtWidgets import QTableWidgetItem
from PyQt5.QtCore import Qt
import sys

CHEK_FILE = 'checkBox.txt'
XLSX = 'statistika.xlsx'
FILE_CTGR = 'Category.xlsx'
HEADERS = {
    'accept': '*/*',
    # 'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.45 Safari/537.36',
'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.93 Safari/537.36 Edg/96.0.1054.53'
}

def get_data():
    t = time.localtime()
    cur_time = time.strftime("%d:%m:%Y", t)
    return cur_time

class Window(QtWidgets.QMainWindow):
    def __init__(self):
        super(Window, self).__init__()
        self.parser = Parsing()
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        self.moves()



    list_all_goods = []
    list_TV = []
    list_Phones = []
    list_all_brands_str = []
    list_all_names_str = []
    list_Phone_brands_str = []
    list_TV_brands_str = []
    list_Phone_norm_name_str = []
    list_TV_norm_name_str = []


    def moves(self):
        self.ui.pushButton.clicked.connect(self.get_all_goods_from_pars)
        self.ui.pushButton_Add_prices.clicked.connect(self.click_add_new_collumn_to_statistika)
        self.ui.pushButton_Category_xlsx.clicked.connect(self.Click_Create_file_Category)
        self.ui.pushButton_Brand_xlsx.clicked.connect(self.Click_Create_file_Brand)
        self.ui.pushButton_Category_table.clicked.connect(self.fill_table_Cat)
        self.ui.pushButton_Brand_table.clicked.connect(self.fill_table_brand)
        self.ui.comboBox_brands.currentTextChanged.connect(self.change_norm_names_list)
        self.ui.comboBox_names.currentTextChanged.connect(self.fill_table_name)
        self.ui.comboBox_Category.currentTextChanged.connect(self.change_all_boxes)
        self.ui.checkBox.stateChanged.connect(self.change_settings_flag)




    def get_all_goods_from_pars(self):
        if self.ui.comboBox_brands.itemText(1) != '':
            return
        self.list_all_goods, self.list_Phones, self.list_TV = self.parser.pars()
        self.list_all_brands_str = self.parser.create_norm_list(self.list_all_goods, 'brand')
        self.list_all_names_str = self.parser.create_norm_list(self.list_all_goods, 'sort_name')
        for i in range(len(self.list_all_brands_str)):
            self.list_all_brands_str[i] = str(self.list_all_brands_str[i])
        for i in range(len(self.list_all_names_str)):
            self.list_all_names_str[i] = str(self.list_all_names_str[i])
        self.ui.comboBox_brands.addItems(self.list_all_brands_str)
        self.ui.comboBox_names.addItems(self.list_all_names_str)

    def click_add_new_collumn_to_statistika(self):
        if len(self.list_all_goods) == 0:
            return
        try:
            open(XLSX)
        except Exception as e:
            self.parser.save_to_xlsx(self.list_all_goods, XLSX)


        df1 = pd.read_excel(XLSX)
        # проверка на повторение даты в последнем столбце
        columns_am = len(df1.columns)
        last_data = df1.columns[columns_am - 1]
        print(last_data)
        if get_data() != last_data:
            # Чтобы цены по товарам не разъезжались
            stat_dict = df1.to_dict()
            price_list = ['no data'] * len(stat_dict['name'])
            cur_data = get_data()
            for i in range(len(stat_dict['name'])):
                for j in range(len(self.list_all_goods)):
                    if stat_dict['name'][i] == self.list_all_goods[j]['name']:
                        price_list[i] = (self.list_all_goods[j][cur_data])  # А точно ли прайс там или ну его нахер?
            df2 = pd.DataFrame(price_list)
            df1[cur_data] = df2
            df1.to_excel(XLSX, index=False)

    def Click_Create_file_Category(self):
        if len(self.list_all_goods) == 0:
            return
        if self.ui.comboBox_Category.currentText() == self.ui.comboBox_Category.itemText(0):
            return
        elif self.ui.comboBox_Category.currentText() == self.ui.comboBox_Category.itemText(1):  #TV
            sort_list = self.parser.sort_name(self.list_TV)
            self.parser.save_to_xlsx(sort_list, FILE_CTGR)
        elif self.ui.comboBox_Category.currentText() == self.ui.comboBox_Category.itemText(2): #Phones
            sort_list = self.parser.sort_name(self.list_Phones)
            self.parser.save_to_xlsx(sort_list, FILE_CTGR)

    def Click_Create_file_Brand(self):
        if len(self.list_all_goods) == 0:
            return
        if self.ui.comboBox_brands.currentText() == self.ui.comboBox_brands.itemText(0):
            return
        list_brand_goods = self.parser.get_all_goods_of_brand(self.list_all_goods, self.ui.comboBox_brands.currentText())
        sort_list = self.parser.sort_name(list_brand_goods)
        df = pd.DataFrame(sort_list)
        df.to_excel(FILE_CTGR, columns=['shop', 'name', get_data()], index=False, sheet_name='Sheet_BR')


    def gen_fill_table(self, goods_list):
        cur_data = get_data()
        self.ui.table.setColumnCount(3)
        self.ui.table.setRowCount(len(goods_list))
        self.ui.table.setHorizontalHeaderLabels(["Shop", "Name", "Price"])
        self.ui.table.horizontalHeaderItem(0).setTextAlignment(Qt.AlignLeft)
        self.ui.table.horizontalHeaderItem(1).setTextAlignment(Qt.AlignHCenter)
        self.ui.table.horizontalHeaderItem(2).setTextAlignment(Qt.AlignRight)
        for i in range(len(goods_list)):
            self.ui.table.setItem(i, 0, QTableWidgetItem(goods_list[i]['shop']))
            self.ui.table.setItem(i, 1, QTableWidgetItem(goods_list[i]['name']))
            self.ui.table.setItem(i, 2, QTableWidgetItem(goods_list[i][cur_data]))
        self.ui.table.resizeColumnsToContents()
        w=0
        for c in range(self.ui.table.columnCount()):
            w = w + self.ui.table.columnWidth(c)
        self.ui.table.resize(int(w + self.ui.table.verticalHeader().width() + self.ui.table.autoScrollMargin() * 1.5),
                             int(self.ui.table.size().height()))

    def fill_table_Cat(self):
        cur_cat = self.ui.comboBox_Category.currentText()
        if cur_cat == 'не выбрано':
            self.ui.table.setRowCount(0)
            return
        elif cur_cat == 'Телевизоры':
            goods_list = self.list_TV
            self.gen_fill_table(goods_list)
        elif cur_cat == 'Смартфоны':
            goods_list = self.list_Phones
            self.gen_fill_table(goods_list)

    def fill_table_brand(self):
        cur_brand = self.ui.comboBox_brands.currentText()
        if cur_brand == 'не выбрано':
            self.ui.table.setRowCount(0)
            return
        goods_list = self.parser.get_all_goods_of_brand(self.list_all_goods, cur_brand)
        self.gen_fill_table(goods_list)

    def fill_table_name(self):
        cur_sort_name = self.ui.comboBox_names.currentText()
        if cur_sort_name == 'не выбрано':
            return
        goods_list = self.parser.get_all_goods_of_sort_name(self.list_all_goods, cur_sort_name)
        self.gen_fill_table(goods_list)

    def change_norm_names_list(self):
        if (self.ui.comboBox_Category.currentText() == 'не выбрано'):
            if (self.ui.comboBox_brands.currentText() == 'не выбрано'):
                list_goods_of_brand = self.list_all_goods
            else:
                list_goods_of_brand = self.parser.get_all_goods_of_brand(self.list_all_goods,
                                                                         self.ui.comboBox_brands.currentText())
        if (self.ui.comboBox_Category.currentText() == 'Телевизоры'):
            if (self.ui.comboBox_brands.currentText() == 'не выбрано'):
                list_goods_of_brand = self.list_TV
            else:
                list_goods_of_brand = self.parser.get_all_goods_of_brand(self.list_TV,
                                                                         self.ui.comboBox_brands.currentText())
        if (self.ui.comboBox_Category.currentText() == 'Смартфоны'):
            if (self.ui.comboBox_brands.currentText() == 'не выбрано'):
                list_goods_of_brand = self.list_Phones
            else:
                list_goods_of_brand = self.parser.get_all_goods_of_brand(self.list_Phones,
                                                                         self.ui.comboBox_brands.currentText())
        for i in range(self.ui.comboBox_names.count() - 1, 0, -1):
            self.ui.comboBox_names.removeItem(i)
        norm_names_of_brand_list = self.parser.create_norm_list(list_goods_of_brand, 'sort_name')
        self.ui.comboBox_names.addItems(norm_names_of_brand_list)
        # for i in range(len(list_goods_of_brand)):
        #     self.ui.comboBox_names.addItem(list_goods_of_brand[i]['sort_name'])


    def change_all_boxes(self):
        # очистка
        for i in range(self.ui.comboBox_brands.count() - 1, 0, -1):
            self.ui.comboBox_brands.removeItem(i)
        for i in range(self.ui.comboBox_names.count() - 1, 0, -1):
            self.ui.comboBox_names.removeItem(i)

        ###
        if self.ui.comboBox_Category.currentText() == 'Смартфоны':
            print('Смартфоны')
            self.list_Phone_brands_str = self.parser.create_norm_list(self.list_Phones, 'brand')
            self.ui.comboBox_brands.addItems(self.list_Phone_brands_str)
            self.list_Phone_norm_name_str = self.parser.create_norm_list(self.list_Phones, 'sort_name')
            self.ui.comboBox_names.addItems(self.list_Phone_norm_name_str)

        elif self.ui.comboBox_Category.currentText() == 'Телевизоры':
            print('иелувизоры')
            self.list_TV_brands_str = self.parser.create_norm_list(self.list_TV, 'brand')
            # for i in range(len(brand_list)):
            #     brand_list[i] = str(brand_list[i])
            self.ui.comboBox_brands.addItems(self.list_TV_brands_str)
            self.list_TV_norm_name_str = self.parser.create_norm_list(self.list_TV, 'sort_name')
            self.ui.comboBox_names.addItems(self.list_TV_norm_name_str)
        else:
            self.ui.comboBox_names.addItems(self.list_all_names_str)
            self.ui.comboBox_brands.addItems(self.list_all_brands_str)

    def change_settings_flag(self):
        with open(CHEK_FILE, 'w') as f:
            if self.ui.checkBox.isChecked():
                f.write('1')
            else:
                f.write('0')

    def test(self):
        self.ui.comboBox_brands.addItem('хаха')
        for i in range(self.ui.comboBox_brands.count()-1, 0, -1):
            self.ui.comboBox_brands.removeItem(i)
        # self.ui.comboBox_names.clear()
    def clear(self):
        for i in range(self.ui.comboBox_brands.count()-1, 0, -1):
            self.ui.comboBox_brands.removeItem(i)


class Parsing():

    def get_html(self, url, params=''):
        resp = requests.get(url, headers=HEADERS, params=params)
        return resp

    def get_goods_WB(self):
        URL_WB_TV = 'https://www.wildberries.ru/catalog/elektronika/tv-audio-foto-video-tehnika/televizory/televizory'
        URL_WB_Phones = 'https://www.wildberries.ru/catalog/elektronika/smartfony-i-telefony/vse-smartfony'

        html_WB_phones = self.get_html(URL_WB_Phones)
        list_WB_Phones = self.get_content_WB_Phones(html_WB_phones.text)

        html_WB_TV = self.get_html(URL_WB_TV)
        list_WB_TV = self.get_content_WB_TV(html_WB_TV.text)
        return list_WB_Phones, list_WB_TV

    def input_brand_WB(self, stroka, label):
        firstpart = stroka[:stroka.index(' ')]
        secondpart = stroka[stroka.index(' '):]
        return firstpart + ' ' + label + secondpart

    def name_for_sorting_WB_Phones(self, full_name):
        if '/' in full_name:
            stroka = full_name[: full_name.index('/') - 1]
            if 'GB' in stroka:
                index_Gb = full_name.index('GB')
                tmp = 0
                for i in range(index_Gb - 1, -1, -1):
                    if full_name[i] != ' ':
                        tmp += 1
                    else:
                        break
                return full_name[:index_Gb - tmp - 1]
            return stroka
        else:
            return full_name

    def get_norm_name_WB_TV(self, name, brand):
        d = name[name.index(' ') + 1:]
        # norm= d[:d.index(' ')]
        if '"' not in d:
            return d.replace("/", "")
        norm = d[:d.index('"') - 6]
        if len(str(norm)) <= 5:
            return d.replace("/", "")
        return 'Телевизор' + ' ' + str(brand) + ' ' + str(norm.replace("/", ""))

    def price_filter_WB(self, item):
        price = item.find('ins', class_='lower-price')
        if price != None:
            return price.get_text()
        else:
            price = item.find('span', class_='lower-price')
            if price != None:
                return price.get_text()
            else:
                return "no price"

    def get_content_WB_Phones(self, html):
        soup = bs4.BeautifulSoup(html, 'html.parser')  # объект html
        items = soup.find_all('div', class_='product-card')
        cards = []

        br = 0
        date = get_data()
        for item in items:
            if br == 20:
                break

            name = item.find('span', class_='goods-name').get_text(strip=True)
            brand = item.find('strong', class_='brand-name').get_text(strip=True).strip('/')
            name = self.input_brand_WB(name, brand)
            cards.append(
                {
                    'name': name,
                    'brand': brand,
                    date: self.price_filter_WB(item),
                    'sort_name': self.name_for_sorting_WB_Phones(name),
                    'shop': 'WB'
                }
            )
            br += 1
        return cards

    def get_content_WB_TV(self, html):
        soup = bs4.BeautifulSoup(html, 'html.parser')
        items = soup.find_all('div', class_='product-card')
        cards = []
        date = get_data()
        br = 0
        for item in items:
            if br == 20:
                break
            name = item.find('span', class_='goods-name').get_text()
            brand = item.find('strong', class_='brand-name').get_text(strip=True).strip('"').strip('/')
            nameBr = self.input_brand_WB(name, brand)
            cards.append(
                {
                    'name': nameBr,
                    'brand': brand,
                    date: self.price_filter_WB(item),
                    'sort_name': self.get_norm_name_WB_TV(name, brand),
                    'shop': 'WB'
                }
            )
            br+=1

        return cards

    def get_goods_CTL(self):
        URL_CTL_TV = 'https://www.citilink.ru/catalog/televizory/'
        URL_CTL_Phones = 'https://www.citilink.ru/catalog/smartfony'

        html_CTL_Phones = self.get_html(URL_CTL_Phones)
        list_CTL_Phones = self.get_content_CTL_Phones(html_CTL_Phones.text)

        html_CTL_TV = self.get_html(URL_CTL_TV)
        list_CTL_TV = self.get_content_CTL_TV(html_CTL_TV.text)
        return list_CTL_Phones, list_CTL_TV

    def name_for_sorting_CTL_Phones(self, full_name):
        index_Gb = full_name.index('Gb')
        tmp = 0
        for i in range(index_Gb - 1, -1, -1):
            if full_name[i] != ' ':
                tmp += 1
            else:
                break
        return full_name[:index_Gb - tmp - 1]

    def price_filter_CTL(self, item):
        price = item.find('span', class_='ProductCardHorizontal__price_current-price')
        if price != None:
            return price.get_text(strip=True).strip('/')
        else:
            return "no price"

    def get_brand_CTL(self, s):
        d = s[s.index(' ') + 1:]  # Из имени брэнд для ситилинка
        f = d[:d.index(' ')]
        return f

    def get_norm_name_CTL_TV(self, name, brand_len):
        if ',' in name:
            norm = name[:name.index(',')]
            return norm
        else:
            return 'untitled'

    def get_content_CTL_Phones(self, html):
        soup = bs4.BeautifulSoup(html, 'html.parser')
        items = soup.find_all('div', class_='product_data__gtm-js')
        # print(items)
        cards = []
        date = get_data()
        k = 0
        for item in items:
            # if k==20:
            #     break
            name = item.find('a', class_='ProductCardHorizontal__title').get_text()
            cards.append(
                {
                    'name': name,
                    'brand': self.get_brand_CTL(name),
                    date: self.price_filter_CTL(item),
                    'sort_name': self.name_for_sorting_CTL_Phones(name),
                    'shop': 'Ситилинк'
                }
            )
            k += 1
        return cards

    def get_content_CTL_TV(self, html):
        soup = bs4.BeautifulSoup(html, 'html.parser')
        items = soup.find_all('div', class_='product_data__gtm-js')
        # print(items)
        cards = []
        date = get_data()
        for item in items:
            name = item.find('a', class_='ProductCardHorizontal__title').get_text()
            brand = self.get_brand_CTL(name);

            cards.append(
                {
                    'name': name,
                    'brand': brand,
                    date: self.price_filter_CTL(item),
                    'sort_name': self.get_norm_name_CTL_TV(name, len(str(brand))),
                    'shop': 'Ситилинк'
                }
            )

        return cards



    def get_goods_ELD(self):
        URL_ELD_TV = 'https://www.eldorado.ru/c/televizory/'
        URL_ELD_Phones = 'https://www.eldorado.ru/c/smartfony/'

        html_ELD_Phones = self.get_html(URL_ELD_Phones)
        list_ELD_Phones = self.get_content_ELD_Phones(html_ELD_Phones.text)

        html_ELD_TV = self.get_html(URL_ELD_TV)
        list_ELD_TV = self.get_content_ELD_TV(html_ELD_TV.text)
        return list_ELD_Phones, list_ELD_TV

    def price_filter_ELD(self, item):
        price = item.find('span', class_='XR')
        if price != None:
            return price.get_text(strip=True).strip('/').strip('.')
        else:
            return "no price"

    def get_content_ELD_Phones(self, html):
        soup = bs4.BeautifulSoup(html, 'html.parser')
        items = soup.find_all('li', class_='jG')
        # print(items)
        cards = []
        date = get_data()
        for item in items:
            name = item.find('a', class_='sG').get_text().strip()
            cards.append(
                {
                    'name': name,
                    'brand': self.get_brand_CTL(name),
                    date: self.price_filter_ELD(item),
                    'sort_name': self.name_for_sorting_ELD_Phones(name),
                    'shop': 'Эльдорадо'
                }
            )
        #print(cards)
        return cards

    def get_content_ELD_TV(self, html):
        soup = bs4.BeautifulSoup(html, 'html.parser')
        items = soup.find_all('li', class_='jG')
        # print(items)
        cards = []
        date = get_data()
        for item in items:
            name = item.find('a', class_='sG').get_text().strip()
            brand = self.get_brand_ELD_TV(name)
            cards.append(
                {
                    'name': name,
                    'brand': brand,
                    date: self.price_filter_ELD(item),
                    'sort_name': self.get_norm_name_ELD_TV(name, len(str(brand))),
                    'shop': 'Эльдорадо'
                }
            )
        #print(cards)
        return cards

    def name_for_sorting_ELD_Phones(self, full_name):
        if 'GB' in full_name:
            index_Gb = full_name.index('GB')
            tmp = 0
            for i in range(index_Gb - 1, -1, -1):
                if full_name[i] != ' ':
                    tmp += 1
                else:
                    break
            return full_name[:index_Gb - tmp - 1]
        else:
            return full_name[:full_name.index('(') - 1]

    def get_brand_ELD_TV(self, name):
        # print(name)
        if '"' in name:
            d = name[name.index('"') + 2:]  # Из имени брэнд tv eldorado
            brand = d[:d.index(' ')]
            return brand
        else:
            return 'zaslaniy kazachok'

    def get_norm_name_ELD_TV(self, name, brand_len):
        if '"' in name:
            norm = 'Телевизор ' + name[name.index('"') + 1:]
            return norm
        else:
            return 'Melechoff'


    def create_norm_list(self, list_cards, key: str):
        itog = []
        for i in range(len(list_cards)):
            if list_cards[i][key] not in itog:
                itog.append(list_cards[i][key])
        return itog


    def pars(self):
        list_goods_WB_Phones, list_goods_WB_TV = self.get_goods_WB()
        list_goods_CTL_Phones, list_goods_CTL_TV = self.get_goods_CTL()
        list_goods_ELD_Phones, list_goods_ELD_TV = self.get_goods_ELD()
        list_all_Phones = list_goods_WB_Phones + list_goods_CTL_Phones + list_goods_ELD_Phones
        list_all_TV = list_goods_WB_TV + list_goods_CTL_TV + list_goods_ELD_TV

        list_all_goods = self.sort_name(list_goods_WB_Phones + list_goods_WB_TV + list_goods_CTL_Phones + list_goods_CTL_TV + list_goods_ELD_Phones + list_goods_ELD_TV)
        return list_all_goods, list_all_Phones, list_all_TV

    def sort_name(self, cards):
        sorted_cards = sorted(cards, key=itemgetter('sort_name'))
        return sorted_cards

    def save_to_xlsx(self, sorted_current_list, path):
        df = pd.DataFrame(sorted_current_list)
        df.to_excel(path, columns=['shop', 'name', get_data()], index=False)

    def get_all_goods_of_brand(self, list_all_goods, brand):
        BRAND = []
        for i in range(len(list_all_goods)):
            if list_all_goods[i]['brand'] == brand:
                BRAND.append(list_all_goods[i])
        return BRAND

    def get_all_goods_of_sort_name(self, list_all_goods, sort_name):
        SORT_NAME = []
        for i in range(len(list_all_goods)):
            if list_all_goods[i]['sort_name'] == sort_name:
                SORT_NAME.append(list_all_goods[i])
        return SORT_NAME

def main():
    print("i work")
    app = QtWidgets.QApplication([])
    application = Window()
    application.show()

    try:
        open(CHEK_FILE)
    except Exception as e:
        open(CHEK_FILE, 'w')
    with open(CHEK_FILE, 'r') as f:
        flag = f.readline()
        if flag == '1':
            application.ui.checkBox.setChecked(1)
        elif flag == '0':
            application.ui.checkBox.setChecked(0)
        else:
            pass

    if (application.ui.checkBox.isChecked()):
        application.get_all_goods_from_pars()



    sys.exit(app.exec_())

#------------------------------------------------------------------------------------------------------------------------------------
#------------------------------------------------------------------------------------------------------------------------------------
if __name__=='__main__':
    main()