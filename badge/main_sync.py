from library.monkeybadge_sync import MonkeyBadge

def main():
    """Entry point"""
    while True:
        badge = MonkeyBadge()
        try:
            badge.run()
        except Exception as err:
            print(f'Error running badge: {err}')


# Run the main function
if __name__ == '__main__':
    print('ENTRY')
    main()
