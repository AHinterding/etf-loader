from etf_mapper.br_loader import BlackRockLoader

if __name__ == '__main__':
    br_loader = BlackRockLoader()
    br_loader.download_compositions_of_country('us')
