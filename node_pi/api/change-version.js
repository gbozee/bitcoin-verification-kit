var b58 = require("bs58check");

const prefixes = new Map([
  ["xpub", "0488b21e"],
  ["ypub", "049d7cb2"],
  ["Ypub", "0295b43f"],
  ["zpub", "04b24746"],
  ["Zpub", "02aa7ed3"],
  ["tpub", "043587cf"],
  ["upub", "044a5262"],
  ["Upub", "024289ef"],
  ["vpub", "045f1cf6"],
  ["Vpub", "02575483"],
]);

const changeVersionBytes = function (xpub, targetFormat) {
  if (!prefixes.has(targetFormat)) {
    return "Invalid target version";
  }

  // trim whitespace
  xpub = xpub.trim();

  try {
    var data = b58.decode(xpub);
    console.log(data);
    data = data.slice(4);
    data = Buffer.concat([
      Buffer.from(prefixes.get(targetFormat), "hex"),
      data,
    ]);
    console.log(data);
    return b58.encode(data);
  } catch (err) {
    return "Invalid extended public key! Please double check that you didn't accidentally paste extra data.";
  }
};

module.exports = (req, res) => {
  let xpub = "";
  let target = "";
  if (req.method === "GET") {
    xpub = req.query.xpub;
    target = req.query.target;
  } else {
    xpub = req.body.xpub;
    target = req.body.target;
  }
  try {
    let result = changeVersionBytes(xpub, target);
    res.status(200).json({ result });
  } catch (error) {
    res.status(400).json({ error: error.message });
  }
};
