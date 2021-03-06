import hashlib

from sawtooth_identity_test.identity_message_factory \
    import IdentityMessageFactory

from sawtooth_processor_test.transaction_processor_test_case \
    import TransactionProcessorTestCase


def _to_hash(value):
    return hashlib.sha256(value).hexdigest()


class TestIdentity(TransactionProcessorTestCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.factory = IdentityMessageFactory()

    def _expect_policy_get(self, key, value=None):
        recieved = self.validator.expect(
            self.factory.create_get_policy_request(key))

        self.validator.respond(
            self.factory.create_get_policy_response(key, value),
            recieved)

    def _expect_role_get(self, key=None, value=None):
        recieved = self.validator.expect(
            self.factory.create_get_role_request(key))

        self.validator.respond(
            self.factory.create_get_role_response(key, value),
            recieved)

    def _expect_policy_set(self, key, expected_value):
        recieved = self.validator.expect(
            self.factory.create_set_policy_request(key, expected_value))

        self.validator.respond(
            self.factory.create_set_policy_response(key),
            recieved)

    def _expect_role_set(self, key, value):
        recieved = self.validator.expect(
            self.factory.create_set_role_request(key, value))

        self.validator.respond(
            self.factory.create_set_role_response(key),
            recieved)

    def _expect_ok(self):
        self.validator.expect(self.factory.create_tp_response("OK"))

    def _expect_invalid_transaction(self):
        self.validator.expect(
            self.factory.create_tp_response("INVALID_TRANSACTION"))

    def _expect_internal_error(self):
        self.validator.expect(
            self.factory.create_tp_response("INTERNAL_ERROR"))

    def _role(self, name, policy_name):
        self.validator.send(self.factory.create_role_transaction(
            name, policy_name))

    def _policy(self, name, declarations):
        self.validator.send(
            self.factory.create_policy_transaction(name, declarations))

    @property
    def _public_key(self):
        return self.factory.public_key

    def test_set_policy(self):
        """
        Tests setting a valid policy.
        """
        self._policy("policy1", "PERMIT_KEY *")
        self._expect_policy_get("policy1")
        self._expect_policy_set("policy1", "PERMIT_KEY *")
        self._expect_ok()

    def test_set_role(self):
        """
        Tests setting a valid role.
        """
        self._role("role1", "policy1")
        self._expect_policy_get("policy1", "PERMIT_KEY *")
        self._expect_role_get("role1")
        self._expect_role_set("role1", "policy1")
        self._expect_ok()

    def test_set_role_without_policy(self):
        """
        Tests setting a invalid role, where the policy does not exist. This
        should return an invalid transaction.
        """
        self._role("role1", "policy1")
        self._expect_policy_get("policy1")
        self._expect_invalid_transaction()

    def test_set_role_without_policy_name(self):
        """
        Tests setting a invalid role, where no policy name is set. This should
        return an invalid transaction.
        """
        self._role("role1", "")
        self._expect_invalid_transaction()

    def test_set_role_without_name(self):
        """
        Tests setting a invalid role, where no role name is set. This should
        return an invalid transaction.
        """
        self._role("", "policy1")
        self._expect_invalid_transaction()

    def test_set_policy_without_entries(self):
        """
        Tests setting a invalid policy, where no entries are set. This
        should return an invalid transaction.
        """
        self._policy("policy1", "")
        self._expect_invalid_transaction()

    def test_set_policy_without_name(self):
        """
        Tests setting a invalid role, where no policy name is set. This should
        return an invalid transaction.
        """
        self._policy("", "PERMIT_KEY *")
        self._expect_invalid_transaction()
