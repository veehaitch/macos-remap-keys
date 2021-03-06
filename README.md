# Remap macOS Keys

Remap keys with pure macOS functionality.

Although the efforts of the [Karabiner-Elements](https://github.com/pqrs-org/Karabiner-Elements)
project are highly appreciated, using it always felt too intrusive and, recently,
also [like a liability](https://github.com/pqrs-org/Karabiner-Elements/issues/2607).
In fact, although quite unknown, if it comes to simple key remapping tasks,
one can use features built directly into macOS.

This project helps in defining remappings easily through a straight-forward configuration file.

## Getting started

Clone this repository and make sure you have Python with `pyyaml` installed.

Edit [`config.yaml`](config.yaml) to your needs.
It has the following structure:

```yaml
keyboard:
  fromKey1: toKey1
  fromKey2: toKey2
  # ...
keypad:
  fromKey1: toKey1
  # ...
```

The `fromKey` and the `toKey` label names correspond to `.keyboard` and `.keypad`
as defined in [`keytables.yaml`](./keytables.yaml).

For example, to remap
<kbd>Caps lock</kbd> to <kbd>Backspace</kbd>, and
<kbd>Backspace</kbd> to <kbd>Delete</kbd>
you have to define `config.yaml` as follows:

```yaml
keyboard:
  Capslock: Backspace
  Backspace: Delete
```

Apply your configuration as follows:

```bash
hidutil property --set `./remap.py --hidutil-property`
```

## Persistent configuration

To keep your remapping configuration in effect across restarts,
you can load it automatically using launchd. To load your configuration
automatically on the next restart, execute the following command:

```bash
./remap.py --launchd-plist ~/Library/LaunchAgents/ch.veehait.macos-remap-keys.plist
```

## Nix?

If you're using Nix with Home Manager on Darwin, you can use something like
the following to manage your mappings. It takes care of applying your remapping
configuration after a `home-manager switch` and also links the launchd plist 
to get picked up on restarts.

```nix
{ config, pkgs, lib, ... }:
let
  macos-remap-keys-flake = builtins.getFlake "github:veehaitch/macos-remap-keys";
  macos-remap-keys = macos-remap-keys-flake.defaultPackage.x86_64-darwin;
  keytables = builtins.toPath "${macos-remap-keys-flake}/keytables.yaml";
  config = pkgs.writeText "macos-remap-config.yaml" (builtins.toJSON {
    keyboard = {
      Capslock = "Backspace";
      Backspace = "Delete";
    };
  });
  macos-remap-launchd = pkgs.runCommand "macos-remap-launchd" { } ''
    mkdir -p $out
    ${macos-remap-keys}/bin/remap.py \
      --config "${config}" \
      --keytables "${keytables}" \
      --launchd-plist \
      "$out/ch.veehait.macos-remap-keys.plist" >/dev/null
  '';
in
{
  # Activate the remappings on switch
  home.activation."macosRemapKeys" = lib.hm.dag.entryAfter ["writeBoundary"] ''
    $DRY_RUN_CMD hidutil property --set \
      `${macos-remap-keys}/bin/remap.py \
      --config ${config} \
      --keytables ${keytables} \
      --hidutil-property` >/dev/null
  '';

  # Activate the remappings on boot
  home.file."Library/LaunchAgents/ch.veehait.macos-remap-keys.plist".source = "${macos-remap-launchd}/ch.veehait.macos-remap-keys.plist";
}
```

## Gruselkabinett

Although very similar, the format demanded by `hidutil` isn't JSON.
For `hidutil property --set` to work, the values of `HIDKeyboardModifierMapping{Src,Dst}`
have to be numbers in their hexadecimal representation. Using a decimal representation,
as supported by JSON, won't work.
That's a weird decision—just Apple things—which demands some Regex string manipulation.

Wonder what would happen if you'd just use a hex string instead of a number?
macOS crashes—completely. Hard to believe?
Go ahead and try it yourself but make sure you don't have any unsaved work:

```bash
hidutil property --set '{"UserKeyMapping":[{"HIDKeyboardModifierMappingSrc":"0x700000039","HIDKeyboardModifierMappingDst":"0x70000002A"}]}'
```

## References / Similar Articles and Projects

- https://developer.apple.com/library/archive/technotes/tn2450/_index.html
- https://dchakarov.com/blog/macbook-remap-keys/
- https://blog.codefront.net/2020/06/24/remapping-keys-on-macos
- https://github.com/amarsyla/hidutil-key-remapping-generator

