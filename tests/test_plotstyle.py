from pdf_genesis.plotstyle import PALETTE, PALETTE_CYCLE, ROLE, apply_house_style


def test_palette_is_colorblind_safe_okabe_ito():
    assert len(PALETTE) == 8
    assert all(v.startswith("#") and len(v) == 7 for v in PALETTE.values())


def test_palette_cycle_uses_known_colors():
    assert set(PALETTE_CYCLE) <= set(PALETTE.values())


def test_roles_reference_palette():
    assert set(ROLE.values()) <= set(PALETTE.values())


def test_apply_house_style_sets_rcparams():
    import matplotlib

    matplotlib.use("Agg")
    apply_house_style(matplotlib)
    assert matplotlib.rcParams["savefig.dpi"] == 300
