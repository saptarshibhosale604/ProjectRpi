from langchain.chat_models import ChatOpenAI
from langchain.prompts import ChatPromptTemplate
from langchain.chains import LLMChain
from langchain.chains.router.multi_prompt_prompt import MULTI_PROMPT_ROUTER_TEMPLATE
from langchain.prompts import PromptTemplate
from langchain.chains.router.llm_router import LLMRouterChain,RouterOutputParser
from langchain.chains.router import MultiPromptChain
import os

# myTestKey07 #saptarshibhosale604@gmail.com
f = open('openai_api_key.txt')
if not os.environ.get("OPENAI_API_KEY"):
  os.environ["OPENAI_API_KEY"] = f.read().strip() 

llm = ChatOpenAI()


beginner_template = '''You are a physics teacher who is really
focused on beginners and explaining complex topics in simple to understand terms. 
You assume no prior knowledge. Give the answer in 5 lines. Here is the question\n{input}'''

expert_template = '''You are a world expert physics professor who explains physics topics
to advanced audience members. You can assume anyone you answer has a 
PhD level understanding of Physics. Give the answer in 5 lines. Here is the question\n{input}'''

prompt_infos = [
    {'name':'advanced physics','description': 'Answers advanced physics questions',
     'prompt_template':expert_template},
    {'name':'beginner physics','description': 'Answers basic beginner physics questions',
     'prompt_template':beginner_template},
]

destination_chains = {}
for p_info in prompt_infos:
    name = p_info["name"]
    prompt_template = p_info["prompt_template"]
    prompt = ChatPromptTemplate.from_template(template=prompt_template)
    chain = LLMChain(llm=llm, prompt=prompt)
    destination_chains[name] = chain

print("\n\n## destination_chains ##:", destination_chains)

# default_prompt = ChatPromptTemplate.from_template("{input}")
# default_chain = LLMChain(llm=llm,prompt=default_prompt)

destinations = [f"{p['name']}: {p['description']}" for p in prompt_infos]
destinations_str = "\n".join(destinations)

print("\n\n## destinations ##:", destinations)
print("\n\n## destinations_str ##:", destinations_str)

router_template = MULTI_PROMPT_ROUTER_TEMPLATE.format(
    destinations=destinations_str
)
router_prompt = PromptTemplate(
    template=router_template,
    input_variables=["input"],
    output_parser=RouterOutputParser(),
)

router_chain = LLMRouterChain.from_llm(llm, router_prompt)
chain = MultiPromptChain(router_chain=router_chain, 
                         destination_chains=destination_chains, 
                         default_chain=default_chain, verbose=True
                        )

print("\n\n## router_chain ##:", router_chain)
print("\n\n## chain ##:", chain)

print("\n\n## How do magnets work? ##:")
chain.run("How do magnets work?")

print("\n\n## what's a quantum entaglement ##:")
chain.run("what's a quantum entaglement?")


