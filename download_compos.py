from etf_mapper import ISharesLoader

if __name__ == '__main__':
    br_loader = ISharesLoader()
    br_loader.download_compositions_of_country('us')
