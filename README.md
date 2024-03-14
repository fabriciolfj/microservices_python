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