import inspect
from faker import Faker

from datagen.model import *
from datagen.provider import *
from datagen.enums import *
from datagen import log


class DataMocker:
    """This is a data mock tools based on faker, with some features extension for graph business scenarios."""

    def __init__(self, locale="en-US", nodes: Dict[NKey, NodeConfig] = None):
        fake: Faker = Faker(locale)
        fake.add_provider(ConstProvider)
        fake.add_provider(ReferenceProvider)
        fake.add_provider(SequenceProvider)
        fake.add_provider(EvalProvider)
        fake.add_provider(OftagProvider(fake, nodes))

        self.fake: Faker = fake
        self.__method_cache = {}

    def mock(self, rule, rule_args=None):
        """This function mocks data by specifying the rule and rule_args.
        :param rule: the generator method name provided by faker object.
        :param rule_args: The parameters required by the selected provider to generate data.
        """

        if rule in self.__method_cache:
            method = self.__method_cache[rule]
        else:
            method = getattr(self.fake, rule)
            self.__method_cache[rule] = method

        if not method:
            raise Exception(f"Unsupported data generate rule: {rule}")

        if type(rule_args) == dict:
            return method(**rule_args)
        else:
            return method()

    def reset(self):
        """For some provider which having status, support cleaning status."""

        seq_provider: SequenceProvider = self.fake.provider("sequence_provider")
        oftag_provider: OftagProvider = self.fake.provider("oftag_provider")
        if seq_provider:
            seq_provider._reset()
        if oftag_provider:
            oftag_provider._reset()
        log.debug(f"Reset status in mocker: {seq_provider}, {oftag_provider}")

    def check_rule(self, rule, rule_args=None):
        """Check if the rule is valid generator and if required parameters are missing"""
        if not hasattr(self.fake, rule):
            raise Exception(f"Unsupported generator of {rule}")

        method = getattr(self.fake, rule)
        params = inspect.signature(method).parameters
        missing_params = [
            p
            for p in params
            if params[p].default == inspect.Parameter.empty
            and params[p].kind
            not in (inspect.Parameter.VAR_POSITIONAL, inspect.Parameter.VAR_KEYWORD)
            and p not in rule_args
        ]
        if missing_params:
            raise Exception(
                f"Generator of {rule} missing required parameters: {','.join(missing_params)}"
            )

        return True
