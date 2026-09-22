// Oak's PIKACHU (IsStarterPikachu) grows like a legendary: CalculateMonStats uses these
// base stats instead of PIKACHU's own (35/55/30/90/50/40, total 300), from the moment
// Oak hands it over. Only the base stats are read from this table.
const struct SpeciesInfo gStarterPikachuBaseStats =
{
    .baseHP        = 100,
    .baseAttack    = 105,
    .baseDefense   =  85,
    .baseSpeed     = 140,
    .baseSpAttack  = 130,
    .baseSpDefense = 100, // total 660
};
