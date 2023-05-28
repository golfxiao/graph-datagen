# There are two ways to generate ids, 0: Auto-increment Sequence 1: Random
ID_MODE_SEQUENCE = 0
ID_MODE_RANDOM = 1

# =================  Rules supported by the genrule configuration item ================#

GENERATOR_ID = "id"  # ID increment sequence，non-repetitive
GENERATOR_INT = "random_int"  # Random integer with special minimum and maximum values, TODO How to support negative numbers?
GENERATOR_NUMBER = "random_number"  # Random integer with special length
GENERATOR_ELEMENT = (
    "random_element"  # Randomly return an element within the specified list range
)
GENERATOR_NAME = "name"  # Person name
GENERATOR_SENTENCE = "sentence"  # Sentence with specified length
GENERATOR_COMPANY = "company"  # Company name
GENERATOR_CONST = "const"  # Constant value
GENERATOR_REFERENCE = "reference"  # Reference variable
GENERATOR_EVAL = "eval"  # Expression
GENERATOR_OFTAG = "oftag"  # Take vertex id from a certain tag, only applicable for the srcVID and dstVID fields of edge.

# ====================  Configuration item name definition for the graph  ==================#
# Schema type definition
SCHEMA_TYPE_VERTEX = "vertex"
SCHEMA_TYPE_EDGE = "edge"

# Predefined properties definition
PROP_VID = "vid"
PROP_SRC_VID = "srcVID"
PROP_DST_VID = "dstVID"
PROP_EDGE_NUM_RULE = "genNumPerVID"
PROP_RANK = "rank"

PREDEFINED_PROPS = [PROP_VID, PROP_SRC_VID, PROP_DST_VID, PROP_RANK, PROP_EDGE_NUM_RULE]

# Property value type definition
VAL_TYPE_INT = "int"
VAL_TYPE_STRING = "string"
VAL_TYPE_FLOAT = "float"
VAL_TYPE_BOOL = "bool"

# Defines the parameters of collection type in the faker generator which need to be converted to collection by eval function.
COLLECTION_PARAMETERS = ["elements"]
