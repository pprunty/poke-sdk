# Submission

## Design Reference

For this project, I referenced some SDKs I used in the past that I had good experience with, namely [OpenAI](https://github.com/openai/openai-python) and [Cloudflare](https://github.com/cloudflare/cloudflare-python/tree/main) - realized afterwards that these APIs used [Stainless](https://www.stainless.com/) to generate their SDKs. I did like the project structure they used though, so referenced that in my development. Namely their use of `resources` and `types` directories, as well as internal files, delimitted by underscores `_` for base and shared classes.

## Why Python?

I used Python because it allowed me to develop faster and I'm more familiar with the libraries there (pytest, pydantic, httpx, etc.). I use Typescript mostly for frontent (Next.js/React). I did consider using Golang as I've started learning that language for [another project](https://github.com/pprunty/magikarp) but it would have taken me too long.

## Architecture

Most design decisions for this assignment are documented or covered in the [./README.md]. Here is a brief summary of tools, libraires and other things I used:

* Makefile - because it makes things easier
* ruff - usually use black+flake8 but discovered ruff during developing this project and works pretty nicely
* Strongly types (py.typed, pydantic) - this is to help IDEs and devlopers using the library. really think python could benefit from going fully typed as a language
* Async/sync usage - yep, this was to support asynchronous calls, maybe not necessary but i guessed it would be handy for somebody using library inside framework like FastAPI where client would be served paginated data 
* Pagination - first time doing this proper but got some help from claude code and found out some new things, like what a 'semaphore' is
* Caching - used cachetools for this, speeds up reserving data very quickly using in memory cache, belive this would be beneficial if serving site like serebii where user will be going back and forth between pokemon in a pokedex and main pokedex listing
* PyPI - didn't push anything to pypi for this, setup some github actions but haven't run anything, maybe could do it in the future
* Tests - i used pytest and pytest-cov (for coverage report) for both unit and integration tests, most tests I used claude code to create whilst developing new parts of the library
* `search` and `pokedex` resources - i found the apis pretty hard to work with if ever i wanted to serve some information on a UI. so i created both a search and pokedex resource, which would amalgamate some API calles to the PokeAPI APIs to do 1. search: for pokemon by ability, type, starts_with and 2. pokedex: custom pokedex for getting a pokemon information by game/generation (like on [serebii.next](https://serebii.next)) - this resource was hacked together using claude code just to have a good use case as part of this submission and can definitely be optimized (it's very slow and too much code), my thinking is somebody using this would benefit by having serebii-like APIs to build their own pokedex site
* `expand()` method on the `_resource.py` - allows users to explore the objects more deeply by fetching apis in named resource with name+url keys for subsequent api direction.

## Challenges

Biggest challenges working with PokeAPI was:

1. The docs site crashes
2. The returned object is large in most cases
3. The return object is a 'graph of hypermedia links' with tons of name/url references to subsequent apis you can call for additional information

To handle (2), I updated the `__repr__` in the [_types.py](./src/poke_sdk/client/_types.py) to have a `_friendly_repr()` method. This prints objects out a little better by default, also allowing user to intutievly see what subsequent APIs can be followed without obsficating the information completely.

To handle (3), I used an `expand()` method in the [_resource.py](./src/poke_sdk/_resource.py) which allows users to explore the objects more deeply. 

I was thinking it would be better to have something like: `bulbasaur = client.pokemon.get(1)` and then `bulbasaur_moves = bulbasaur.moves.list()` but everywhere I read online said that betrays SDK design standards. It would also be complex to develop.