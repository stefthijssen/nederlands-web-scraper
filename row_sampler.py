import sys, json, random

def sample_rows(file, amount):
    with open(file) as jf:
        data = json.load(jf)
        nf = open("sample_output.txt", "w")
        nf.write('begin')
        for idx, element in enumerate(random.sample(data, amount)):
            nf.write(f"{idx+1}: {element['siteUrl']}\n")
        nf.close()
        

def main(argv):
    sample_rows(str(argv[0]), int(argv[1]))


if __name__ == "__main__":
    main(sys.argv[1:])