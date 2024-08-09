# GSL
Gecko's Scripting Language

GSL is a simple, embeddable language that is compiled to custom bytecode (Azure Leaf VM) on the fly.

# Warning
GSL is nowhere close to something that resembles a working language. A lot of stuff is not implemented right now, there is no standard library, there's basically nothing - main task was to build the whole chain and compile 'hello, world' program - once I figure stuff out I'll start working more intensively on this.

# Setting up and launching
Clone the repo and run `./gsl examples/example_hw.gsl` for hello world.

# Embedding
TODO

# Contributing
TODO

# Roadmap
- [ ] Definition of the language and its grammar
- [ ] Full coverage of language's syntax
- [ ] Somewhat complete stdlib
- [ ] Refactoring for adequate error handling (e.g. lexer, parser, compiler errors)
- [ ] Finish the roadmap

# Licensing
This project is licensed under GNU LGPL v3, see LICENSE file.