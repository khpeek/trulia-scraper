import math
from pyparsing import Word, nums, Literal

def parse_results(string):
	'''Parse the string "1 - 30 of 1048" on the landing page to get the numbers 30 (listings per page) and 1048 (total number of listings)'''
	num = Word(nums).setParseAction(lambda s,l,t: [int(t[0])])
	expression = Literal("1") + "-" + num("number_per_page") + "of" + num("total_number") + "Results"
	result = expression.parseString(string)
	return result["number_per_page"], result["total_number"]

def number_of_pages_to_scrape(number_per_page, total_number):
	return math.ceil(total_number/number_per_page)

def get_number_of_pages_to_scrape(string):
	return number_of_pages_to_scrape(*parse_results(string))