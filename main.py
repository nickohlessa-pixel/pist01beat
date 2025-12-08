from pist01beat import Pist01Beat

def main():
    model = Pist01Beat()
    result = model.predict("HOR", "DEN")
    print(result)

if __name__ == "__main__":
    main()
