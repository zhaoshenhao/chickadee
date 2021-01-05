import file

def demo():
    j = file.load_json('/dat/config.json')
    print(j)
    file.dump_json(j, '/test.json')

if __name__ == "__main__":
    demo()
