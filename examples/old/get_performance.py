from api.sigma import TradeTwoSigma

if __name__ == '__main__':
    two = TradeTwoSigma('8a6b5c00-78eb-4a16-a02a-658800f8be28').get_performance(output_return=True, verbose=True)

    print(two)

    # print(TradeTwoSigma('8a6b5c00-78eb-4a16-a02a-658800f8be28').get_positions(get_all=True))
