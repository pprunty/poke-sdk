# Submission

For this project, I referenced some SDKs I used in the past that I had good experience with, namely [OpenAI](https://github.com/openai/openai-python) and [Cloudflare](https://github.com/cloudflare/cloudflare-python/tree/main) - realized afterwards that these APIs used [Stainless](https://www.stainless.com/) to generate their APIs. I did like the project structure they used though, so referenced that in my development. Namely their use of `resources` and `types` directories, as well as internal files, delimitted by underscores `_` for base and shared classes.

I used Python because it allowed me to develop faster and I'm more familiar with libraries there (pytest, pydantic, httpx, etc.). I mostly code Typescript for frontent (Next.js/React). I did consider using Golang as I've started learning that language for [another project](https://github.com/pprunty/magikarp) but would have taken me too long.


* Makefile
* black/flake8
* Strongly types (py.typed, pydantic)
* Async/sync usage
* Pagination
* Caching
