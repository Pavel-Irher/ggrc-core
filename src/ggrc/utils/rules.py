# Copyright (C) 2020 Google Inc.
# Licensed under http://www.apache.org/licenses/LICENSE-2.0 <see LICENSE file>

"""Mapping rules for Relationship validation and map:model import columns."""

import collections
import functools

from ggrc.utils import helpers


class ImmutableDict(collections.Mapping):
  """An immutable wrapper for defaultdict with False by default."""

  __slots__ = ("_dict", "_hash")
  DEFAULT_VALUE = False

  def __init__(self, **kwargs):
    super(ImmutableDict, self).__init__()
    self._dict = collections.defaultdict(lambda: self.DEFAULT_VALUE)
    self._hash = None
    self._update(**kwargs)

  def _update(self, *args, **kwargs):
    """Update internal dict."""
    self._dict.update(*args, **kwargs)

  def __getitem__(self, key):
    """Passthrough to internal dict."""
    return self._dict[key]

  def __iter__(self):
    """Passthrough to internal dict."""
    return self._dict.__iter__()

  def __len__(self):
    """Passthrough to internal dict."""
    return self._dict.__len__()

  def __hash__(self):
    """Hash of own values (computed lazily)."""
    if self._hash is None:
      self._hash = hash(frozenset(self._dict.iteritems()))
    return self._hash

  def __eq__(self, other):
    """True if other is instance of self.__class__ and has same _dict."""
    # pylint: disable=protected-access; we check other to be of same type first
    return isinstance(other, self.__class__) and self._dict == other._dict

  def __repr__(self):
    return "{cls}(**{arg})".format(cls=self.__class__.__name__,
                                   arg=dict(self._dict))


class Labels(object):  # pylint: disable=too-few-public-methods
  """Enum with labels used as MappingRule keys."""
  MAP = "map"
  UNMAP = "unmap"
  TYPE = "type"
  MAP_SNAPSHOT = "map_snapshot"


class BasicRule(ImmutableDict):
  """Passes cls.VALUE to ImmutableDict."""

  VALUE = {}

  def __init__(self, type_):
    value = {Labels.TYPE: type_}
    value.update(self.VALUE)
    super(BasicRule, self).__init__(**value)


class MappingRule(BasicRule):
  """Boolean flags for mappings."""

  VALUE = {Labels.MAP: True,
           Labels.UNMAP: True}


class StaticMappingRule(BasicRule):
  """Boolean flags to only show mapped objects."""

  VALUE = {Labels.MAP: True}


class SnapshotMappingRule(MappingRule):
  """Boolean flags to map snapshots."""

  VALUE = {Labels.MAP_SNAPSHOT: True}


class StaticSnapshotMappingRule(MappingRule):
  """Boolean flags to only show mapped snapshots."""

  VALUE = {Labels.MAP_SNAPSHOT: True}


class IssueMappingRule(MappingRule):
  """Boolean flags to allow to map/unmap original objects and snapshots."""

  VALUE = {Labels.MAP: True,
           Labels.UNMAP: True,
           Labels.MAP_SNAPSHOT: True}


def wrap_rules(func):
  """Transform str-type rules into MappingRule(str)."""
  def make_rules(items):
    """For all non-BasicRule items, replace them with MappingRule(item)."""
    for item in items:
      if not isinstance(item, BasicRule):
        item = MappingRule(type_=item)
      yield item

  @functools.wraps(func)
  def inner(*args, **kwargs):
    """Transform func result {key: {rule}} -> {key: {rule.type: rule}}."""
    result = func(*args, **kwargs)
    return {key: set(make_rules(value))
            for (key, value) in result.iteritems()}

  return inner


@helpers.cached
@wrap_rules
def _all_rules():
  """Get mapping, unmapping and snapshot mapping rules.

  Special cases:
    Audit has direct mapping to Program with program_id
    Assessment has direct mapping to Audit as well as Relationship
  """
  from ggrc import snapshotter

  all_models = {'AccessGroup', 'Contract', 'Control',
                'CycleTaskGroupObjectTask', 'DataAsset', 'Facility', 'Issue',
                'Market', 'Objective', 'OrgGroup',
                'Policy', 'Process', 'Product', 'Program', 'Project',
                'Regulation', 'Risk', 'Requirement', 'Standard',
                'System', 'Threat', 'Vendor', 'Metric', 'ProductGroup',
                'TechnologyEnvironment', 'KeyReport', 'AccountBalance'}

  snapshots = snapshotter.rules.Types.all

  all_rules = {
      "AccessGroup": all_models - {'AccessGroup'},
      "AccountBalance": all_models,
      "Contract": all_models - {'Contract'},
      "Control": all_models,
      "CycleTaskGroupObjectTask": ((all_models | {'Audit'}) -
                                   {'CycleTaskGroupObjectTask'}),
      "TaskGroup": all_models - {'CycleTaskGroupObjectTask'},
      "DataAsset": all_models,
      "Facility": all_models,
      "Market": all_models,
      "Objective": all_models,
      "OrgGroup": all_models,
      "Person": all_models,
      "Policy": all_models - {'Policy'},
      "Process": all_models,
      "Product": all_models,
      "Program": all_models - {'Program'},
      "Project": all_models,
      "Regulation": all_models - {'Regulation'},
      "Risk": all_models - {'Risk'},
      "Requirement": all_models,
      "Standard": all_models - {'Standard'},
      "System": all_models,
      "TechnologyEnvironment": all_models,
      "Threat": all_models - {'Threat'},
      "Vendor": all_models,
      "Metric": all_models,
      "ProductGroup": all_models,
      "KeyReport": all_models,
  }

  # Audit and Audit-scope objects
  # Assessment has a special Audit field instead of map:audit

  all_rules.update({
      "Audit": {StaticMappingRule("Assessment"), "Issue"} | {
          StaticSnapshotMappingRule(type_) for type_ in snapshots
      },
      "Assessment": {"Issue"} | {
          StaticSnapshotMappingRule(type_) for type_ in snapshots
      },
      "Issue": {"Assessment", "Audit", "CycleTaskGroupObjectTask", "Issue",
                "Program", "Project"} | {
          IssueMappingRule(type_) for type_ in snapshots
      },
  })

  return all_rules


def _filter_rules(rules, flag):
  """Get rule.type_ for each rule[flag] == True."""
  return {key: {rule[Labels.TYPE] for rule in value if rule[flag]}
          for (key, value) in rules.iteritems()}


@helpers.cached
def get_mapping_rules():
  return _filter_rules(_all_rules(), Labels.MAP)


@helpers.cached
def get_unmapping_rules():
  return _filter_rules(_all_rules(), Labels.UNMAP)


@helpers.cached
def get_snapshot_mapping_rules():
  return _filter_rules(_all_rules(), Labels.MAP_SNAPSHOT)


__all__ = [
    "get_mapping_rules",
    "get_snapshot_mapping_rules",
    "get_unmapping_rules",
]
