
        contract Token {
            mapping(address => uint) public balances;
            
            // INTENTIONAL VULNERABILITY: No check for overflow (if older solidity) or arbitrary minting
            function mint(address to, uint amount) public {
                balances[to] += amount;
            }
        }
        