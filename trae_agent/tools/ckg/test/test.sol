// SPDX-License-Identifier: MIT
pragma solidity ^0.8.19;

/**
 * Solidity Language Test File
 * Tests all structural elements supported by the Solidity parser
 */

// Import statements
import "@openzeppelin/contracts/token/ERC20/ERC20.sol";
import "@openzeppelin/contracts/access/Ownable.sol";
import "./interfaces/ITestInterface.sol";

// Library definition
library MathLib {
    function sqrt(uint256 x) internal pure returns (uint256) {
        if (x == 0) return 0;
        uint256 z = (x + 1) / 2;
        uint256 y = x;
        while (z < y) {
            y = z;
            z = (x / z + z) / 2;
        }
        return y;
    }

    function max(uint256 a, uint256 b) internal pure returns (uint256) {
        return a >= b ? a : b;
    }

    function min(uint256 a, uint256 b) internal pure returns (uint256) {
        return a < b ? a : b;
    }
}

// Interface definition
interface ITokenVault {
    event Deposit(address indexed user, uint256 amount);
    event Withdrawal(address indexed user, uint256 amount);
    
    function deposit(uint256 amount) external;
    function withdraw(uint256 amount) external;
    function balanceOf(address user) external view returns (uint256);
    function totalSupply() external view returns (uint256);
}

// Abstract contract
abstract contract BaseVault {
    mapping(address => uint256) internal _balances;
    uint256 internal _totalSupply;

    modifier nonZeroAmount(uint256 amount) {
        require(amount > 0, "Amount must be greater than zero");
        _;
    }

    function _updateBalance(address user, uint256 newBalance) internal virtual {
        uint256 oldBalance = _balances[user];
        _balances[user] = newBalance;
        _totalSupply = _totalSupply - oldBalance + newBalance;
    }

    function totalSupply() public view virtual returns (uint256) {
        return _totalSupply;
    }
}

// Enum definition
enum VaultStatus {
    INACTIVE,
    ACTIVE,
    PAUSED,
    EMERGENCY_STOPPED
}

// Struct definition
struct UserInfo {
    uint256 balance;
    uint256 lastDeposit;
    uint256 rewardDebt;
    bool isVip;
}

struct PoolInfo {
    address token;
    uint256 allocPoint;
    uint256 lastRewardBlock;
    uint256 accRewardPerShare;
    uint256 totalStaked;
}

// Error definitions (custom errors)
error InsufficientBalance(uint256 requested, uint256 available);
error UnauthorizedAccess(address caller);
error VaultPaused();
error InvalidAmount(uint256 amount);

// Main contract
contract TokenVault is BaseVault, ITokenVault, Ownable, ERC20 {
    using MathLib for uint256;

    // State variables
    mapping(address => UserInfo) public userInfo;
    mapping(address => bool) public isWhitelisted;
    PoolInfo[] public poolInfo;
    
    uint256 public constant MAX_SUPPLY = 1000000 * 10**18;
    uint256 public immutable DEPLOYMENT_TIME;
    
    VaultStatus public status;
    address public feeCollector;
    uint256 public feeRate = 100; // 1%
    
    // Events
    event StatusChanged(VaultStatus oldStatus, VaultStatus newStatus);
    event FeeCollectorUpdated(address indexed oldCollector, address indexed newCollector);
    event UserWhitelisted(address indexed user, bool whitelisted);
    event PoolAdded(address indexed token, uint256 allocPoint);
    event RewardsDistributed(address indexed user, uint256 amount);

    // Modifiers
    modifier onlyActive() {
        if (status != VaultStatus.ACTIVE) {
            revert VaultPaused();
        }
        _;
    }

    modifier onlyWhitelisted() {
        require(isWhitelisted[msg.sender], "Not whitelisted");
        _;
    }

    modifier validAddress(address addr) {
        require(addr != address(0), "Invalid address");
        _;
    }

    // Constructor
    constructor(
        string memory name,
        string memory symbol,
        address _feeCollector
    ) ERC20(name, symbol) Ownable(msg.sender) {
        DEPLOYMENT_TIME = block.timestamp;
        feeCollector = _feeCollector;
        status = VaultStatus.ACTIVE;
        
        // Initialize first pool
        poolInfo.push(PoolInfo({
            token: address(this),
            allocPoint: 1000,
            lastRewardBlock: block.number,
            accRewardPerShare: 0,
            totalStaked: 0
        }));
        
        emit PoolAdded(address(this), 1000);
    }

    // External functions
    function deposit(uint256 amount) 
        external 
        override 
        onlyActive 
        nonZeroAmount(amount) 
    {
        UserInfo storage user = userInfo[msg.sender];
        
        if (user.balance + amount > MAX_SUPPLY) {
            revert InvalidAmount(amount);
        }
        
        // Transfer tokens from user
        _transfer(msg.sender, address(this), amount);
        
        // Update user balance
        user.balance += amount;
        user.lastDeposit = block.timestamp;
        
        // Update pool info
        _updateBalance(msg.sender, user.balance);
        
        emit Deposit(msg.sender, amount);
    }

    function withdraw(uint256 amount) 
        external 
        override 
        onlyActive 
        nonZeroAmount(amount) 
    {
        UserInfo storage user = userInfo[msg.sender];
        
        if (user.balance < amount) {
            revert InsufficientBalance(amount, user.balance);
        }
        
        // Calculate fee
        uint256 fee = (amount * feeRate) / 10000;
        uint256 withdrawAmount = amount - fee;
        
        // Update user balance
        user.balance -= amount;
        _updateBalance(msg.sender, user.balance);
        
        // Transfer tokens
        _transfer(address(this), msg.sender, withdrawAmount);
        if (fee > 0) {
            _transfer(address(this), feeCollector, fee);
        }
        
        emit Withdrawal(msg.sender, withdrawAmount);
    }

    function balanceOf(address user) 
        external 
        view 
        override 
        returns (uint256) 
    {
        return userInfo[user].balance;
    }

    // Public functions
    function addPool(
        address token,
        uint256 allocPoint
    ) public onlyOwner validAddress(token) {
        poolInfo.push(PoolInfo({
            token: token,
            allocPoint: allocPoint,
            lastRewardBlock: block.number,
            accRewardPerShare: 0,
            totalStaked: 0
        }));
        
        emit PoolAdded(token, allocPoint);
    }

    function updateStatus(VaultStatus newStatus) public onlyOwner {
        VaultStatus oldStatus = status;
        status = newStatus;
        emit StatusChanged(oldStatus, newStatus);
    }

    function setWhitelist(address user, bool whitelisted) 
        public 
        onlyOwner 
        validAddress(user) 
    {
        isWhitelisted[user] = whitelisted;
        emit UserWhitelisted(user, whitelisted);
    }

    function setFeeCollector(address newCollector) 
        public 
        onlyOwner 
        validAddress(newCollector) 
    {
        address oldCollector = feeCollector;
        feeCollector = newCollector;
        emit FeeCollectorUpdated(oldCollector, newCollector);
    }

    // Internal functions
    function _distributeBatchRewards(address[] memory users) internal {
        for (uint256 i = 0; i < users.length; i++) {
            address user = users[i];
            UserInfo storage userStruct = userInfo[user];
            
            if (userStruct.balance > 0) {
                uint256 reward = _calculateReward(user);
                if (reward > 0) {
                    userStruct.rewardDebt += reward;
                    emit RewardsDistributed(user, reward);
                }
            }
        }
    }

    function _calculateReward(address user) internal view returns (uint256) {
        UserInfo storage userStruct = userInfo[user];
        uint256 timeElapsed = block.timestamp - userStruct.lastDeposit;
        
        if (timeElapsed < 1 days || userStruct.balance == 0) {
            return 0;
        }
        
        // Simple reward calculation: 1% daily
        return (userStruct.balance * timeElapsed) / (365 days * 100);
    }

    // View functions
    function getPoolCount() external view returns (uint256) {
        return poolInfo.length;
    }

    function getPoolInfo(uint256 poolId) 
        external 
        view 
        returns (PoolInfo memory) 
    {
        require(poolId < poolInfo.length, "Pool does not exist");
        return poolInfo[poolId];
    }

    function getUserInfo(address user) 
        external 
        view 
        returns (UserInfo memory) 
    {
        return userInfo[user];
    }

    function canWithdraw(address user, uint256 amount) 
        external 
        view 
        returns (bool) 
    {
        return userInfo[user].balance >= amount && 
               status == VaultStatus.ACTIVE;
    }

    // Fallback and receive functions
    receive() external payable {
        revert("Direct ETH transfers not allowed");
    }

    fallback() external payable {
        revert("Function not found");
    }

    // Override required by multiple inheritance
    function totalSupply() 
        public 
        view 
        override(BaseVault, ERC20) 
        returns (uint256) 
    {
        return BaseVault.totalSupply();
    }
}

// Additional contract for testing inheritance
contract VaultFactory {
    event VaultCreated(address indexed vault, address indexed owner);
    
    mapping(address => address[]) public ownerVaults;
    address[] public allVaults;
    
    function createVault(
        string memory name,
        string memory symbol,
        address feeCollector
    ) external returns (address) {
        TokenVault vault = new TokenVault(name, symbol, feeCollector);
        
        ownerVaults[msg.sender].push(address(vault));
        allVaults.push(address(vault));
        
        emit VaultCreated(address(vault), msg.sender);
        return address(vault);
    }
    
    function getOwnerVaults(address owner) 
        external 
        view 
        returns (address[] memory) 
    {
        return ownerVaults[owner];
    }
    
    function getAllVaults() external view returns (address[] memory) {
        return allVaults;
    }
}
