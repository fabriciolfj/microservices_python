# Microservices python
- para iniciar o aplicativo:
```
pip install env
pip install fastapi uvicorn
pip install pipenv
pipenv shell
uvicorn orders.app:app --reload
```

- para iniciar o kitchen que utiliza o flask
```
 pipenv install flask-smorest
 pip install flask-smorest
 flask run --reload
```

- o orm utilizado é o sqlalchemy e o migration alembic
- para criar a pasta de migrations:
````
alembic init migrations
````
- para gerar as tabelas com base no orm
````
PYTHONPATH=`pwd` alembic revision --autogenerate -m "Initial migration"
````
- para aplicar
````
PYTHONPATH=`pwd` alembic upgrade heads
````

- para iniciar o mock
 - usamos o prism
 - prism mock open_api.yaml  --port 3000


# GraphQL
- Representação
```
type Cake implements ProductInterface {
  id: ID!
  name: String!
  price: Float
  available: Boolean!
  hasFilling: Boolean!
  hasNutsToppingOption: Boolean!
  lastUpdated: Datetime!
  ingredients: [IngredientRecipe!]!
}
 
type Beverage implements ProductInterface {
  id: ID!
  name: String!
  price: Float
  available: Boolean!
  hasCreamOnTopOption: Boolean!
  hasServeOnIceOption: Boolean!
  lastUpdated: Datetime!
  ingredients: [IngredientRecipe!]!
}
 
union Product = Beverage | Cake
```
- Query
```
input ProductsFilter {
  maxPrice: Float
  minPrice: Float
  available: Boolean = true,
  sort: SortingOrder = DESCENDING
  resultsPerPage: Int = 10
  page: Int = 1
}
 

type Query {
  allProducts: [Product!]!
  allIngredients: [Ingredient!]!
  products(input: ProductsFilter!): [Product!]!
  product(id: ID!): Product
  ingredient(id: ID!): Ingredient
}
```
- Mutation
```
enum ProductType {
  cake
  beverage
}
 
input IngredientRecipeInput {
  ingredient: ID!
  quantity: Float!
  unit: MeasureUnit!
}
 
enum Sizes {
  SMALL
  MEDIUM
  BIG
}
 
type Mutation {
  addProduct(
    name: String!
    type: ProductType!
    price: String
    size: Sizes
    ingredients: [IngredientRecipeInput!]! 
    hasFilling: Boolean = false
    hasNutsToppingOption: Boolean = false
    hasCreamOnTopOption: Boolean = false
    hasServeOnIceOption: Boolean = false
  ): Product!
}
```
- usando o graphql fake
```
npm install graphql-faker

./node_modules/.bin/graphql-faker schema.graphql

ou 

docker run -v=${PWD}:/workdir -p=9002:9002 apisguru/graphql-faker schema.graphql

```
- expões os seguintes endpotins:
  - /editor Um editor interativo onde você pode desenvolver sua API GraphQL.
  - /graphql Uma interface GraphiQL para sua API GraphQL. Esta é a interface que usaremos para explorar a API e executar nossas consultas.
  - /voyager Uma exibição interativa de sua API, que ajuda você a entender os relacionamentos e dependências entre seus tipos.
- Consulta de um objeto union, onde devemos especificar o que queremos de cada implementação
```
{
  allProducts {
    ...commonProperties
    ...cakeProperties
    ...beverageProperties
  }
}
fragment commonProperties on ProductInterface {
  name
}
 
fragment cakeProperties on Cake {
  hasFilling
}
 
fragment beverageProperties on Beverage {
  hasCreamOnTopOption
}
```
- usando objetos como parâmetros de entrada para consulta
```
{
  products(input: {maxPrice: 10}) {
    ...on ProductInterface {
      name
    }
  }
}
```
- criando consultas com objetos alinhados
````
{
  allProducts {
    ...on ProductInterface {
      name
      ingredients {
        ingredient {
          name
          supplier {
            name
          }
        }
      }
    }
  }
}
````
- executando múltiplas consultas na mesma requisição
```
{
  allProducts {
    ...commonProperties
  }
  allIngredients {
    name
  }
}
 
fragment commonProperties on ProductInterface {
  name
}
```
- usando alias
```
{
# alias              funcao 
  availableProducts: products(input: {available: true}) {
    ...commonProperties
  }
  unavailableProducts: products(input: {available: false}) {
    ...commonProperties
  }
}
 
 # retorno, o que queremos
fragment commonProperties on ProductInterface {
  name
}
```
- exemplo de mutation
```
# chamada
mutation {
  addProduct(name: "Mocha", type: beverage, input: {price: 10, size: BIG, ingredients: [{ingredient: 1, quantity: 1, unit: LITERS}]}) {
    ...commonProperties
  }
}

#  response, o que queremos
fragment commonProperties on ProductInterface {
  name
}

```
- montando um wrapper para casos onde temos muitos parâmetros envolvidos na função
```
# Query document
mutation CreateAndDeleteProduct(
  $name: String!
  $type: ProductType!
  $input: AddProductInput!
  $id: ID!
) {
  addProduct(name: $name, type: $type, input: $input) {
    ...commonProperties
  }
  deleteProduct(id: $id)
}
 
fragment commonProperties on ProductInterface {
  name
}


# na sessão de query variables

{
  "name": "Mocha",
  "type": "beverage",
  "input": {
    "price": 10,
    "size": "BIG",
    "ingredients": [{"ingredient": 1, "quantity": 1, "unit": "LITERS"}]
  },
  "id": "asdf"
}
```
- podemos fazer solicitações http para a api graphql (apenas get para querys ou post para mutatons), exemplo:
```
curl http://localhost:9002/graphql --data-urlencode     'query={allIngredients{name}}'
```

# Implementando graphql no pyhton usando ariadne
- projeto product
- criamos o serviro e o schema
- dentro do schame vinculamos os resolvedores para query, mutation e types
- como ariadne utiliza documentação, no próprio schema adicionamos o arquivo .graphql da doc, para assim demonstrar o que espera como parâmetro, retorno e as operações
- o que é um resolvedor?
  - é uma função que sabe como processar a solicitação para uma determinada query ou mutation
  - para registrar um resolvedor, usamos as classes QueryType ou MutationType
  - podemos ter resolvedores de tipo, seja escalares ou tipo de atributo customizavel.