from langchain.document_loaders import CSVLoader

loader = CSVLoader('./penguins.csv')

data = loader.load()

# print(data)

print("type::",type(data))

print("data0::",data[0])

print("data1::",data[1])

print("data0content::",data[0].page_content)
