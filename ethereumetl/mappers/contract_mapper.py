from ethereumetl.domain.EthContract import EthContract


class EthContractMapper(object):

    def rpc_result_to_receipt(self, contract_address, rpc_result):
        contract = EthContract()
        contract.address = contract_address
        contract.code = rpc_result

        return contract

    def contract_to_dict(self, contract):
        return {
            'type': 'contract',
            'contract_address': contract.address,
            'contract_code': contract.code
        }
